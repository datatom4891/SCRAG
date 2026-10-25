from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langsmith import traceable


from agent.agent_state import CRAGAgentState
from agent.kb import KnowledgeBase
from agent.config import VectorIndexConfig, LLMConfig, TavilyToolConfig
from agent.prompts import ContextRelevancePrompt, QuestionRefinementPrompt, AnswerPrompt
from agent.models import ContextRelevance, RAGAnswer, RefinedQuestion


# load_dotenv(override=True)


class ContextRetrievalNode:
    def __init__(self, vector_index_config: VectorIndexConfig):
        self.vector_store = KnowledgeBase(vector_index_config) 

    @traceable(name="context_retrieval_node")
    def __call__(self, state: CRAGAgentState):
        kb = self.vector_store
        query = state.question
        
        context = kb.doc_retriever(query)
        
        return {"context":context}

class ContextCriticNode:
    def __init__(self, llm_config: LLMConfig):
            self.llm = init_chat_model(llm_config.model_name, 
                                       temperature=llm_config.temperature, 
                                       max_tokens= llm_config.max_tokens)
    
    @traceable(name="context_critic_node")
    def __call__(self, state:CRAGAgentState):
        question = state.question
        retrieved_docs = state.context
        
        crp = ContextRelevancePrompt()
        
        structured_llm_context_judge = self.llm.with_structured_output(ContextRelevance)
        web_search = False
        relevant_docs =[]
        
        for doc in retrieved_docs:
            crp_prompt = crp.prompt_template.format(user_question=question, retrieved_context=doc)
            critic = structured_llm_context_judge.invoke(crp_prompt)
            
            if critic.relevance_score > 3:
                relevant_docs.append(doc)
            else:
                web_search = True
        return {"context":relevant_docs, "augment_with_web_search":web_search}
        
        
class DecisionRouter:
    def __init__(self):
        pass
    
    @traceable(name="question_refinement_or_not_node")
    def __call__(self, state: CRAGAgentState):
        if state.augment_with_web_search:
            return "refine_question"
        else:
            return "answer"

class QuestionRefinementNode:
    def __init__(self, llm_config: LLMConfig):
        self.llm = init_chat_model(llm_config.model_name, 
                                   temperature=llm_config.temperature, 
                                   max_tokens= llm_config.max_tokens)

    @traceable(name="question_refinement_node")
    def __call__(self, state: CRAGAgentState):
        query = state.question
        structured_llm_refine_question = self.llm.with_structured_output(RefinedQuestion)

        qrp = QuestionRefinementPrompt()
        qrp_prompt = qrp.prompt_template.format(user_question=query,)
        response = structured_llm_refine_question.invoke(qrp_prompt )
        optimized_query = response.refined_question

        return {"refined_question": optimized_query}

class WebSearchNode:
    def __init__(self, tavily_config: TavilyToolConfig):
        self.search_tool = TavilySearch(max_results=tavily_config.max_results, topic = tavily_config.topic)
    
    def _search_web(self, query, initial_context_size):
        results =[]
        i = initial_context_size
        raw_search_results = self.search_tool.invoke({"query":query})

        # TavilySearch returns a plain message string instead of a dict when no results are found
        if isinstance(raw_search_results, str):
            return results

        for rsr in raw_search_results.get("results", []):
            source = rsr["url"]
            content = rsr["content"]
            results.append(f"[Article Source {i}: {source}]\n\n {content}")
            i = i + 1
        
        return results
    
    def __call__(self, state:CRAGAgentState):
        search_query = state.refined_question
        docs = state.context
        docs.extend(self._search_web(search_query, len(docs)))
        
        return {"context":docs}
        

class AnswerNode:
    def __init__(self, llm_config: LLMConfig):
        self.llm = init_chat_model(llm_config.model_name, 
                                   temperature=llm_config.temperature, 
                                   max_tokens= llm_config.max_tokens)
        self.structured_llm_rag_answer = self.llm.with_structured_output(RAGAnswer)
    
    def _format_retrived_docs(self, doc_list):
        return "\n\n-----------------------------------------------------------\n\n".join(doc_list)

    @traceable(name="answer_generation_node")
    def __call__(self, state: CRAGAgentState):
        query = state.question

        context = state.context
        formatted_context = self._format_retrived_docs(context)
        ap = AnswerPrompt()
        ap_prompt = ap.prompt_template.format(user_question=query, retrieved_context=formatted_context)
        response = self.structured_llm_rag_answer.invoke(ap_prompt)
        return {"rag_response": response.answer}
        
