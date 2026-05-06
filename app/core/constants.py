NODE_STATUS_MAP = {
    "router_node": "intent_analysis",
    "router_started": "intent_analysis",
    "vision_node": "vision_analysis",
    "retrieval_node": "retrieving_code",
    "retrieve_code": "retrieving_code",
    "retrieving_code": "retrieving_code",
    "tool_agent_node": "planning",
    "tool_agent_planned": "planning",
    "tool_agent_execution": "tool_agent_execution",
    "generate_answer": "generating_answer",
    "generation_started": "generating_answer",
    "safe_tools": "tool_agent_execution",
    "sensitive_tools": "security_approval",
    "expert_review_node": "expert_review",
    "expert_review_started": "expert_review",
    "finalize_answer": "final_response"
}
