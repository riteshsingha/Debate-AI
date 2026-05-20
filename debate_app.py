from __future__ import annotations
import re
from typing import TypedDict, List, Literal

from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


# STATE DEFINITION

class DebateState(TypedDict):
    topic: str
    round: int
    max_rounds: int

    pro_history: List[str]
    con_history: List[str]
    judge_history: List[str]

    last_pro: str
    last_con: str
    last_judge: str

    score_pro: int
    score_con: int

# MODELS

# PRO: OPENAI
pro_llm = ChatOpenAI(
    model="gpt-5",
    temperature=0.7,
    timeout=60,
    max_retries=2,
)

# CON: GEMINI
con_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.7,
    timeout=60,
    max_retries=2,
)

# JUDGE: OPENAI
judge_llm = ChatOpenAI(
    model="gpt-5.4",
    temperature=0.7,
    timeout=60,
    max_retries=2,
)

# HELPERS

Winner = Literal["PRO", "CON", "UNKNOWN"]

def parse_winner(text: str) -> Winner:
    """
    Expected first line: Winner: PRO|CON
    """

    m = re.search(r"Winner\s*:\s*(PRO|CON)\b", text, re.IGNORECASE)
    if not m:
        return "UNKNOWN"
    return m.group(1).upper()

def pretty_block(title: str, content: str) -> str:
    bar = "=" * 72
    return f"\n{bar}\n{title}\n{bar}\n{content.strip()}"

# NODE FUNCTIONS

def pro_node(state: DebateState) -> DebateState:
    topic = state["topic"]
    r = state["round"]

    PRO_PROMPT = f"""
    You are a Debator PRO. Support the claim.

    Topic: {topic}
    Round: {r} of {state["max_rounds"]}

    Debate Rules:
    - 5 lines
    - If CON argued before, rebut it
    - No personal attacks
    - Be crisp and technical when applicable

    CON last argument:
    {state["last_con"]}

    JUDGE feedback last round:
    {state["last_judge"]}

    Write PRO argument now.
    """
    response = pro_llm.invoke(PRO_PROMPT).content

    state["last_pro"] = response
    state["pro_history"].append(f"Round {r} (PRO):\n{response}")
    return state

def con_node(state: DebateState) -> DebateState:
    topic = state["topic"]
    r = state["round"]

    CON_PROMPT = f"""
    You are a Debator CON. Oppose the claim.

    Topic: {topic}
    Round: {r} of {state["max_rounds"]}

    Debate Rules:
    - 5 lines
    - Directly rebut PRO
    - No personal attacks
    - Highlight risks, edge cases, hidden costs

    PRO last argument:
    {state["last_pro"]}

    JUDGE feedback last round:
    {state["last_judge"]}

    Write CON argument now.
    """
    response = con_llm.invoke(CON_PROMPT).content[0]["text"]

    state["last_con"] = response
    state["con_history"].append(f"Round {r} (CON):\n{response}")
    return state

def judge_node(state: DebateState) -> DebateState:
    topic = state["topic"]
    r = state["round"]

    JUDGE_PROMPT = f"""
    You are the JUDGE of this Debate. Evaluate this round strictly without any biasing.

    Topic: {topic}
    Round: {r} of {state["max_rounds"]}

    PRO argument:
    {state["last_pro"]}

    CON argument:
    {state["last_con"]}

    Rules:
    - Pick a winner based on: logic, rebuttal quality, clarity, factual discipline
    - Be brief
    - Output EXACTLY this format:

    Winner: PRO|CON
    Reason: <2-4 line>
    """
    response = judge_llm.invoke(JUDGE_PROMPT).content.strip()

    winner = parse_winner(response)

    if winner == "PRO":
        state["score_pro"] += 1
    elif winner == "CON":
        state["score_con"] += 1
    
    state["last_judge"] = response
    state["judge_history"].append(f"Round {r} (JUDGE):\n{response}")
    return state

def route_after_judge(state: DebateState) -> str:
    if state["round"] >= state["max_rounds"]:
        return "final_round"
    return "next_round"

def next_round_node(state: DebateState) -> DebateState:
    state["round"] += 1
    return state

def final_node(state: DebateState) -> DebateState:
    topic = state["topic"]
    score_pro = state["score_pro"]
    score_con = state["score_con"]

    if score_pro > score_con:
        final_winner = "PRO"
    elif score_pro < score_con:
        final_winner = "CON"
    else:
        final_winner = "DRAW"

    judge_summary = "\n\n".join(state["judge_history"])

    prompt = f"""
            You are teh FINAL JUDGE. Provide final verdict.

            Topic: {topic}

            Round decisions: {judge_summary}

            Return EXACTLY:

            Final Winner: PRO|CON|DRAW
            Final Score: PRO {score_pro} - CON {score_con}
            Conclusion: <5-6 lines balanced conclusion + why winner won>
        """
    response = judge_llm.invoke(prompt).content.strip()
    state["judge_history"].append(f"FINAL VERDICT:\n{response}")
    state["last_judge"] = response
    return state

# BUILD LANGGRAPH
def build_graph():
    graph_builder = StateGraph(DebateState)

    graph_builder.add_node("pro", pro_node)
    graph_builder.add_node("con", con_node)
    graph_builder.add_node("judge", judge_node)
    graph_builder.add_node("next_round", next_round_node)
    graph_builder.add_node("final_round", final_node)

    graph_builder.set_entry_point("pro")
    graph_builder.add_edge("pro", "con")
    graph_builder.add_edge("con", "judge")

    #CONDITIONAL ROUTING AFTER JUDGE (LOOP OR END)
    graph_builder.add_conditional_edges("judge", route_after_judge,
        {
            "next_round": "next_round",
            "final_round": "final_round",
        },
    )

    graph_builder.add_edge("next_round","pro")
    graph_builder.add_edge("final_round", END)

    graph = graph_builder.compile()

    return graph

# RUN THE CODE
if __name__ == "__main__":
    topic = input("Enter a debate topic: ").strip()

    app = build_graph()

    state: DebateState = {
        "topic": topic,
        "round": 1,
        "max_rounds": 3,
        "pro_history": [],
        "con_history": [],
        "judge_history": [],
        "last_pro": "",
        "last_con": "",
        "last_judge": "",
        "score_pro": 0,
        "score_con": 0,
    }

    final_state = None
    for step in app.stream(state):
        node_name, node_state = next(iter(step.items()))
        r = node_state["round"]

        if node_name == "pro":
            print(pretty_block(f"ROUND {r} - PRO", node_state["last_pro"]))
        elif node_name == "con":
            print(pretty_block(f"ROUND {r} - CON", node_state["last_con"]))
        elif node_name == "judge":
            print(pretty_block(f"ROUND {r} - JUDGE", node_state["last_judge"]))
        elif node_name == "final_round":
            print(pretty_block("FINAL VERDICT", node_state["last_judge"]))

        final_state = node_state