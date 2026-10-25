from dataclasses import dataclass

@dataclass
class SCRAGAgentState:
    question: str | None
    refined_question: str | None = None
    context: str | None = None
    context_critic: str | None = None
    context_relevance_rank: int | None = None
    rag_response: str | None = None
    route: str | None = None
    question_refined_counter: int = 0
    
