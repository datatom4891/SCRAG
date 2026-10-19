from langgraph.graph import StateGraph, START, END
from agent_nodes import *
from agent_state import SCRAGAgentState
from config import RAGAgentConfig


class SCRAGAgent:
    def __init__(self, config:RAGAgentConfig):
      self.agent_config = config
      self.scrag_agent = self._build_agent()
      
      
      
    def _build_agent(self):
      retreival_node = ContextRetrievalNode(self.agent_config.vector_index_config)
      judge_node = ContextCriticNode(self.agent_config.llm_config)
      decision_router = DecisionRouter()
      answer_node = AnswerNode(self.agent_config.llm_config)
      question_refinement_node = QuestionRefinementNode(self.agent_config.llm_config)
      
      graph = StateGraph(SCRAGAgentState)
      graph.add_node("retrieval_node", retreival_node)
      graph.add_node("judge_node", judge_node)
      graph.add_node("answer_node", answer_node)
      graph.add_node("question_refinement_node", question_refinement_node)
      
      graph.add_edge(START, "retrieval_node")
      graph.add_edge("retrieval_node", "judge_node")
      graph.add_conditional_edges("judge_node", decision_router, {"answer":"answer_node",
                                                                "refine_question":"question_refinement_node"})
      graph.add_edge("question_refinement_node", "retrieval_node")
      graph.add_edge("answer_node", END)
      
      app = graph.compile()
      return app
    
    def ask_agent(self, question):
        response = self.scrag_agent.invoke({"question": question})
        return response["rag_response"]