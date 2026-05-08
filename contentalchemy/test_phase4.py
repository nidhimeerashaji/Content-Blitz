from src.workflow.langgraph_workflow import workflow

def run_test(label, user_input, expected_agent):
    print(f"\n{'='*55}")
    print(f"Test:     {label}")
    print(f"Input:    {user_input}")

    result = workflow.invoke({
        "messages":        [],
        "user_input":      user_input,
        "next_agent":      "",
        "agent_chain":     [],
        "topic":           "",
        "research_output": None,
        "blog_output":     None,
        "linkedin_output": None,
        "image_prompt":    None,
        "final_output":    None,
        "error":           None,
    })

    print(f"Routed:   {result['next_agent']}")
    print(f"Chain:    {result['agent_chain']}")
    print(f"Topic:    {result['topic']}")
    print(f"Error:    {result['error']}")
    print(f"\nOutput preview:\n{result['final_output'][:400]}...")

    # Check research was used by blog if chained
    if "research" in expected_agent and result.get("blog_output"):
        print(f"\n✅ Research fed into blog successfully")

# Single agent tests
run_test("Single research",  "Research the future of AI",         "research")
run_test("Single blog",      "Write a blog about climate change",  "blog")
run_test("Single linkedin",  "LinkedIn post about productivity",   "linkedin")

# Chained agent tests
run_test(
    "Research → Blog chain",
    "Research remote work trends then write a blog post about it",
    "research→blog"
)
run_test(
    "Research → LinkedIn chain",
    "Research AI in healthcare and create a linkedin post about it",
    "research→linkedin"
)
run_test(
    "Blog → LinkedIn chain",
    "Write a blog about leadership then make a linkedin post from it",
    "blog→linkedin"
)