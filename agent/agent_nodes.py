from langchain.chat_models import init_chat_model
from langsmith import traceable


from agent.agent_state import SCRAGAgentState
from agent.kb import KnowledgeBase
from agent.config import VectorIndexConfig, EmbeddingConfig, VectorStoreConfig, LLMConfig
from agent.prompts import ContextRelevancePrompt, QuestionRefinementPrompt, AnswerPrompt
from agent.models import ContextRelevance, RAGAnswer


# load_dotenv(override=True)


class ContextRetrievalNode:
    def __init__(self, vector_index_config: VectorIndexConfig):
        self.vector_store = KnowledgeBase(vector_index_config) 

    @traceable(name="context_retrieval_node")
    def __call__(self, state: SCRAGAgentState):
        kb = self.vector_store
        if state.question_refined_counter > 0:
            query = state.refined_question
        else:
            query = state.question
        
        context = kb.doc_retriever(query)
        
        return {"context":context}

class ContextCriticNode:
    def __init__(self, llm_config: LLMConfig):
        self.llm = init_chat_model(llm_config.model_name, temperature=llm_config.temperature, max_tokens= llm_config.max_tokens)
    
    @traceable(name="context_critic_node")
    def __call__(self, state:SCRAGAgentState):
        vector_index_config = VectorIndexConfig()
        
        crp = ContextRelevancePrompt()
        kb = KnowledgeBase(vector_index_config)
        structured_llm_context_judge = self.llm.with_structured_output(ContextRelevance)
        
        
        
        if state.question_refined_counter > 0:
            query = state.refined_question
        else:
            query = state.question
        
        retrieved_context = kb.doc_retriever(query)
        
        crp_prompt = crp.prompt_template.format(user_question=query, retrieved_context=retrieved_context)
        response = structured_llm_context_judge.invoke(crp_prompt)
        
        return {
          "context_relevance_rank":response.relevance_score,
          "context_critic":response.reason
        }
        
class DecisionRouter:
    def __init__(self):
        pass

    def __call__(self, state: SCRAGAgentState):
        max_refinements = 3
        score = state.context_relevance_rank

        if state.question_refined_counter > max_refinements:
            return "answer"

        if score is None:
            return "refine_question"

        if not isinstance(score, (int, float)):
            return "refine_question"

        if score >= 4:
            return "answer"

        return "refine_question"

class QuestionRefinementNode:
    def __init__(self, llm_config: LLMConfig):
        self.llm = init_chat_model(llm_config.model_name, temperature=llm_config.temperature, max_tokens= llm_config.max_tokens)

    @traceable(name="question_refinement_node")
    def __call__(self, state: SCRAGAgentState):
        if state.question_refined_counter > 0:
            query = state.refined_question
        else:
            query = state.question

        qrp = QuestionRefinementPrompt()
        qrp_prompt = qrp.prompt_template.format(user_question=query, context_critic_reason=state.context_critic)
        response = self.llm.invoke(qrp_prompt )
        return {"refined_question": response, "question_refined_counter": state.question_refined_counter + 1}

class AnswerNode:
    def __init__(self, llm_config: LLMConfig):
        self.llm = init_chat_model(llm_config.model_name, temperature=llm_config.temperature, max_tokens= llm_config.max_tokens)
        self.structured_llm_rag_answer = self.llm.with_structured_output(RAGAnswer)

    @traceable(name="answer_generation_node")
    def __call__(self, state: SCRAGAgentState):
        if state.question_refined_counter > 0:
            query = state.refined_question
        else:
            query = state.question

        context = state.context
        ap = AnswerPrompt()
        ap_prompt = ap.prompt_template.format(user_question=query, retrieved_context=context)
        response = self.structured_llm_rag_answer.invoke(ap_prompt)
        return {"rag_response": response.answer}
        
