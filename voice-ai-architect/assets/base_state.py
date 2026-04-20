from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Optimized Memory: Keep only recent turns to save tokens
    recent_messages: Annotated[list[BaseMessage], add_messages]
    
    # State Compression: A rolling summary of the conversation
    conversation_summary: str
    
    # Routing Tracker
    current_node: str
    
    # Business Logic & CRM Action Tracking (flags instead of nested dicts)
    crm_action_pending: bool
    api_latency_flag: bool # Triggers stall fillers if API is slow
    
    # Edge Cases & Guardrails
    objection_count: int
    barge_in_type: str # 'backchannel' or 'interruption'