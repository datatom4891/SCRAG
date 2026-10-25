from dataclasses import dataclass, field

@dataclass
class SCRAGAgentState:
    question: str | None
    refined_question: str | None = None
    context: list[str] | None = None
    context_critic: str | None = None
    context_relevance_rank: int | None = None
    rag_response: str | None = None
    route: str | None = None
    question_refined_counter: int = 0
    
@dataclass
class CRAGAgentState:
    question: str | None
    refined_question: str | None = None
    context: list[str] =  field(default_factory=list)
    augment_with_web_search: bool | None = None