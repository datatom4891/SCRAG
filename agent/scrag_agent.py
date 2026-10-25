from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass
from agent.agent_nodes import ContextCriticNode, ContextRetrievalNode, DecisionRouter, AnswerNode, QuestionRefinementNode, WebSearchNode
from agent.agent_state import SCRAGAgentState
from agent.config import RAGAgentConfig, TavilyToolConfig
from agent.security.security_pipeline  import SecurityPipeline

@dataclass
class SCRAGResponse:
    security_breach: bool
    agent_response: str

class SCRAGAgent:
    def __init__(self, config: RAGAgentConfig):
      self.security_pipeline = SecurityPipeline() 
      self.agent_config = config
      self.scrag_agent = self._build_agent()
      
      
      
    def _build_agent(self):
      retrieval_node = ContextRetrievalNode(self.agent_config.vector_index_config)
      judge_node = ContextCriticNode(self.agent_config.llm_config)
      decision_router_node = DecisionRouter()
      web_search_node = WebSearchNode(self.agent_config.tavily_config)
      answer_node = AnswerNode(self.agent_config.llm_config)
      question_refinement_node = QuestionRefinementNode(self.agent_config.llm_config)
      
      graph = StateGraph(SCRAGAgentState)
      graph.add_node("retrieval_node", retrieval_node)
      graph.add_node("judge_node", judge_node)
      graph.add_node("question_refinement_node", question_refinement_node)
      graph.add_node("web_search_node", web_search_node)
      graph.add_node("answer_node", answer_node)
      
      graph.add_edge(START, "retrieval_node")
      graph.add_edge("retrieval_node", "judge_node")
      graph.add_conditional_edges("judge_node", decision_router_node, {"answer":"answer_node",
                                                                "refine_question":"question_refinement_node"})
      graph.add_edge("question_refinement_node", "web_search_node")
      graph.add_edge("web_search_node","answer_node")
      graph.add_edge("answer_node", END)
      
      app = graph.compile()
      
      graph_png_bytes = app.get_graph().draw_mermaid_png()
      with open("crag_graph.png","wb") as f:
        f.write(graph_png_bytes)
      
      return app
    
    def ask_agent(self, question: str) -> SCRAGResponse:
        sanitization_response = self.security_pipeline.process_user_input(question)
        
        if sanitization_response.failed_injection_check is False:
            user_question = sanitization_response.sanitized_text
            response = self.scrag_agent.invoke({"question": user_question })
            agent_response = SCRAGResponse(
              security_breach = sanitization_response.failed_injection_check,
              agent_response = response["rag_response"]
            )
            return agent_response
        else:
            agent_response = SCRAGResponse(
                          security_breach = sanitization_response.failed_injection_check,
                          agent_response = "Attempted security breach, access blocked"
                        )
            return agent_response