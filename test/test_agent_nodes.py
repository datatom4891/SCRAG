from unittest.mock import MagicMock, patch

import pytest

from agent.agent_nodes import (
    AnswerNode,
    ContextCriticNode,
    ContextRetrievalNode,
    DecisionRouter,
    QuestionRefinementNode,
    WebSearchNode,
)
from agent.agent_state import CRAGAgentState
from agent.config import LLMConfig, TavilyToolConfig, VectorIndexConfig
from agent.models import ContextRelevance, RAGAnswer, RefinedQuestion


@pytest.fixture
def llm_config():
    return LLMConfig(model_name="gpt-4o-mini", temperature=0, max_tokens=256)


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.with_structured_output.return_value = MagicMock()
    return llm


def _critic_score(score: int) -> ContextRelevance:
    return ContextRelevance(relevance_score=score, reason="because")


# ---------------------------------------------------------------------------
# ContextRetrievalNode
# ---------------------------------------------------------------------------

def test_context_retrieval_node_creates_knowledge_base_from_config():
    config = VectorIndexConfig()

    with patch("agent.agent_nodes.KnowledgeBase") as kb_cls:
        ContextRetrievalNode(config)

    kb_cls.assert_called_once_with(config)


def test_context_retrieval_node_returns_retrieved_context():
    config = VectorIndexConfig()

    with patch("agent.agent_nodes.KnowledgeBase") as kb_cls:
        kb_cls.return_value.doc_retriever.return_value = ["doc A", "doc B"]
        node = ContextRetrievalNode(config)

    state = CRAGAgentState(question="What is Green Lantern?")
    result = node(state)

    node.vector_store.doc_retriever.assert_called_once_with("What is Green Lantern?")
    assert result == {"context": ["doc A", "doc B"]}


def test_context_retrieval_node_returns_formatter_output_when_nothing_found():
    with patch("agent.agent_nodes.KnowledgeBase") as kb_cls:
        kb_cls.return_value.doc_retriever.return_value = "No relevant documents found"
        node = ContextRetrievalNode(VectorIndexConfig())

    result = node(CRAGAgentState(question="unknown topic"))

    assert result == {"context": "No relevant documents found"}


# ---------------------------------------------------------------------------
# ContextCriticNode
# ---------------------------------------------------------------------------

def test_context_critic_node_initializes_chat_model_with_llm_config(llm_config):
    with patch("agent.agent_nodes.init_chat_model") as init_model:
        ContextCriticNode(llm_config)

    init_model.assert_called_once_with(
        "gpt-4o-mini", temperature=0, max_tokens=256
    )


def test_context_critic_node_keeps_docs_scored_above_three(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = ContextCriticNode(llm_config)

    structured = mock_llm.with_structured_output.return_value
    structured.invoke.side_effect = [_critic_score(5), _critic_score(4)]

    state = CRAGAgentState(question="q", context=["doc 1", "doc 2"])
    result = node(state)

    mock_llm.with_structured_output.assert_called_with(ContextRelevance)
    assert result == {"context": ["doc 1", "doc 2"], "augment_with_web_search": False}


def test_context_critic_node_filters_low_scoring_docs_and_flags_web_search(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = ContextCriticNode(llm_config)

    structured = mock_llm.with_structured_output.return_value
    structured.invoke.side_effect = [_critic_score(5), _critic_score(2), _critic_score(4)]

    state = CRAGAgentState(question="q", context=["good", "bad", "also good"])
    result = node(state)

    assert result == {"context": ["good", "also good"], "augment_with_web_search": True}


def test_context_critic_node_treats_score_of_three_as_not_relevant(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = ContextCriticNode(llm_config)

    structured = mock_llm.with_structured_output.return_value
    structured.invoke.return_value = _critic_score(3)

    result = node(CRAGAgentState(question="q", context=["borderline"]))

    assert result == {"context": [], "augment_with_web_search": True}


def test_context_critic_node_flags_web_search_when_all_docs_irrelevant(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = ContextCriticNode(llm_config)

    structured = mock_llm.with_structured_output.return_value
    structured.invoke.return_value = _critic_score(1)

    result = node(CRAGAgentState(question="q", context=["x", "y"]))

    assert result == {"context": [], "augment_with_web_search": True}


def test_context_critic_node_with_no_docs_does_not_flag_web_search(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = ContextCriticNode(llm_config)

    structured = mock_llm.with_structured_output.return_value

    result = node(CRAGAgentState(question="q", context=[]))

    structured.invoke.assert_not_called()
    assert result == {"context": [], "augment_with_web_search": False}


def test_context_critic_node_judges_each_doc_against_question(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = ContextCriticNode(llm_config)

    structured = mock_llm.with_structured_output.return_value
    structured.invoke.return_value = _critic_score(5)

    node(CRAGAgentState(question="Who is Hal Jordan?", context=["Hal is a pilot."]))

    prompt_sent = structured.invoke.call_args.args[0]
    assert "Who is Hal Jordan?" in prompt_sent
    assert "Hal is a pilot." in prompt_sent


# ---------------------------------------------------------------------------
# DecisionRouter
# ---------------------------------------------------------------------------

def test_decision_router_routes_to_refinement_when_web_search_needed():
    router = DecisionRouter()

    state = CRAGAgentState(question="q", augment_with_web_search=True)

    assert router(state) == "refine_question"


def test_decision_router_routes_to_answer_when_web_search_not_needed():
    router = DecisionRouter()

    state = CRAGAgentState(question="q", augment_with_web_search=False)

    assert router(state) == "answer"


def test_decision_router_routes_to_answer_when_flag_unset():
    router = DecisionRouter()

    state = CRAGAgentState(question="q")

    assert router(state) == "answer"


# ---------------------------------------------------------------------------
# QuestionRefinementNode
# ---------------------------------------------------------------------------

def test_question_refinement_node_initializes_chat_model_with_llm_config(llm_config):
    with patch("agent.agent_nodes.init_chat_model") as init_model:
        QuestionRefinementNode(llm_config)

    init_model.assert_called_once_with(
        "gpt-4o-mini", temperature=0, max_tokens=256
    )


def test_question_refinement_node_invokes_llm_with_formatted_prompt(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = QuestionRefinementNode(llm_config)

    structured = mock_llm.with_structured_output.return_value
    structured.invoke.return_value = RefinedQuestion(refined_question="refined query")

    node(CRAGAgentState(question="original question"))

    mock_llm.with_structured_output.assert_called_with(RefinedQuestion)
    prompt_sent = structured.invoke.call_args.args[0]
    assert "original question" in prompt_sent
    assert "{{user_question}}" not in prompt_sent


def test_question_refinement_node_returns_refined_question_text(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = QuestionRefinementNode(llm_config)

    structured = mock_llm.with_structured_output.return_value
    structured.invoke.return_value = RefinedQuestion(refined_question="refined query")

    result = node(CRAGAgentState(question="q"))

    assert result == {"refined_question": "refined query"}


# ---------------------------------------------------------------------------
# WebSearchNode
# ---------------------------------------------------------------------------

def test_web_search_node_builds_tavily_search_tool():
    with patch("agent.agent_nodes.TavilySearch") as tavily_cls:
        WebSearchNode(TavilyToolConfig())

    tavily_cls.assert_called_once_with(max_results=3, topic="general")


def test_web_search_node_formats_results_with_source_numbering():
    with patch("agent.agent_nodes.TavilySearch") as tavily_cls:
        tavily_cls.return_value.invoke.return_value = {
            "query": "query",
            "results": [
                {"url": "https://a.example", "content": "first body"},
                {"url": "https://b.example", "content": "second body"},
            ],
        }
        node = WebSearchNode(TavilyToolConfig())

    formatted = node._search_web("query", initial_context_size=2)

    node.search_tool.invoke.assert_called_once_with({"query": "query"})
    assert formatted == [
        "[Article Source 2: https://a.example]\n\n first body",
        "[Article Source 3: https://b.example]\n\n second body",
    ]


def test_web_search_node_handles_plain_string_response_from_tavily():
    with patch("agent.agent_nodes.TavilySearch") as tavily_cls:
        tavily_cls.return_value.invoke.return_value = (
            "No search results found for 'query'. Try modifying your search parameters."
        )
        node = WebSearchNode(TavilyToolConfig())

    formatted = node._search_web("query", initial_context_size=0)

    assert formatted == []


def test_web_search_node_appends_web_results_to_existing_context():
    with patch("agent.agent_nodes.TavilySearch") as tavily_cls:
        tavily_cls.return_value.invoke.return_value = {
            "query": "refined q",
            "results": [
                {"url": "https://web.example", "content": "web body"},
            ],
        }
        node = WebSearchNode(TavilyToolConfig())

    state = CRAGAgentState(
        question="q",
        refined_question="refined q",
        context=["existing doc"],
    )
    result = node(state)

    node.search_tool.invoke.assert_called_once_with({"query": "refined q"})
    assert result == {
        "context": [
            "existing doc",
            "[Article Source 1: https://web.example]\n\n web body",
        ]
    }


def test_web_search_node_with_no_results_leaves_context_unchanged():
    with patch("agent.agent_nodes.TavilySearch") as tavily_cls:
        tavily_cls.return_value.invoke.return_value = {"query": "refined", "results": []}
        node = WebSearchNode(TavilyToolConfig())

    state = CRAGAgentState(question="q", refined_question="refined", context=["kept"])
    result = node(state)

    assert result == {"context": ["kept"]}


# ---------------------------------------------------------------------------
# AnswerNode
# ---------------------------------------------------------------------------

def test_answer_node_initializes_chat_model_and_structured_output(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm) as init_model:
        node = AnswerNode(llm_config)

    init_model.assert_called_once_with("gpt-4o-mini", temperature=0, max_tokens=256)
    mock_llm.with_structured_output.assert_called_once_with(RAGAnswer)
    assert node.structured_llm_rag_answer is mock_llm.with_structured_output.return_value


def test_answer_node_joins_docs_with_separator(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = AnswerNode(llm_config)

    formatted = node._format_retrived_docs(["doc 1", "doc 2", "doc 3"])

    separator = "\n\n-----------------------------------------------------------\n\n"
    assert formatted == separator.join(["doc 1", "doc 2", "doc 3"])


def test_answer_node_formats_empty_docs_as_empty_string(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = AnswerNode(llm_config)

    assert node._format_retrived_docs([]) == ""


def test_answer_node_returns_answer_text_from_structured_response(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = AnswerNode(llm_config)

    structured = mock_llm.with_structured_output.return_value
    structured.invoke.return_value = RAGAnswer(answer="Hal Jordan is a test pilot.")

    state = CRAGAgentState(question="Who is Hal Jordan?", context=["Hal is a test pilot."])
    result = node(state)

    assert result == {"rag_response": "Hal Jordan is a test pilot."}


def test_answer_node_prompt_contains_question_and_joined_context(llm_config, mock_llm):
    with patch("agent.agent_nodes.init_chat_model", return_value=mock_llm):
        node = AnswerNode(llm_config)

    structured = mock_llm.with_structured_output.return_value
    structured.invoke.return_value = RAGAnswer(answer="ok")

    state = CRAGAgentState(question="my question", context=["context one", "context two"])
    node(state)

    prompt_sent = structured.invoke.call_args.args[0]
    assert "my question" in prompt_sent
    assert "context one" in prompt_sent
    assert "context two" in prompt_sent
    assert "{user_question}" not in prompt_sent
    assert "{retrieved_context}" not in prompt_sent
