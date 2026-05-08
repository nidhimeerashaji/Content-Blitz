from src.workflow.langgraph_workflow import workflow

print("Script started")  # add this as line 1

from src.workflow.langgraph_workflow import workflow

print("Workflow imported")  # add this

test_cases = [
    "Write a blog post about the future of AI",
    "I need a LinkedIn post about remote work trends",
    "Research the latest electric vehicle statistics",
    "Create an image of a futuristic office",
    "Build me a content calendar for next month",
]



for user_input in test_cases:
    result = workflow.invoke({
        "messages": [],
        "user_input": user_input,
        "next_agent": "",
        "topic": "",
        "research_output": None,
        "blog_output": None,
        "linkedin_output": None,
        "image_prompt": None,
        "final_output": None,
        "error": None,
    })
    print(f"Input:  {user_input[:50]}")
    print(f"Routed: {result['next_agent']} | Topic: {result['topic']}")
    print(f"Output: {result['final_output']}\n")