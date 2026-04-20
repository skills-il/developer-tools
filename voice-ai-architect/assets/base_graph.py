from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# TODO: The LLM should import the actual project state
# from state import AgentState 

# --- 1. Node Definitions ---
def conversational_node(state: dict) -> dict:
    """
    Template for a standard voice node handling user intent.
    LLM must implement specific system prompts and structured output logic here.
    """
    return {"current_node": "conversational_node"}

def pre_tts_validator_node(state: dict) -> dict:
    """
    GUARDRAIL: Intercepts LLM response before TTS.
    Strips hallucinations (e.g., Markdown, explicitly generated prices).
    """
    # LLM will inject regex or basic validation logic here
    return {"current_node": "validator"}

# --- 2. Routing Logic ---
def route_conversation(state: dict) -> Literal["conversational_node", "pre_tts_validator_node", "__end__"]:
    """
    Template router. The LLM must replace this with actual business logic routing
    based on the state variables.
    """
    if state.get("crm_action_pending"):
         # Example routing logic
         pass
         
    return "pre_tts_validator_node"

# --- 3. Graph Construction ---
def build_graph():
    # LLM should replace 'dict' with 'AgentState' when generating the real graph
    builder = StateGraph(dict) 

    # Add Nodes
    builder.add_node("conversational_node", conversational_node)
    builder.add_node("pre_tts_validator_node", pre_tts_validator_node)

    # Add Edges
    builder.add_edge(START, "conversational_node")
    
    # Add Conditional Edges
    builder.add_conditional_edges(
        "conversational_node",
        route_conversation
    )
    
    # The Validator MUST be an exit-only node leading to END
    builder.add_edge("pre_tts_validator_node", END)

    # Compile the graph with memory
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    
    return graph