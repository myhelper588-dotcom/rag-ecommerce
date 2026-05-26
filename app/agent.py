import os
from typing import TypedDict, Annotated
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from tools.rag_tool import rag_search, init_vectorstore
from tools.calculator_tool import calculate
from tools.shopify_tool import shopify_get_products, shopify_get_orders
from tools.database_tool import query_database

# ============================================================
# CONFIGURATION LLM
# ============================================================
llm = ChatAnthropic(model="claude-opus-4-5")
tools = [rag_search, calculate, shopify_get_products, shopify_get_orders, query_database]
llm_with_tools = llm.bind_tools(tools)

# ============================================================
# SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = """Tu es un assistant expert eCommerce.
Tu as accès à des outils — utilise-les systématiquement :

- rag_search : documents internes, politiques, procédures
- calculate : tout calcul financier, marge, pourcentage, perte
- shopify_get_products : catalogue, stock, prix, variantes
- shopify_get_orders : commandes, CA, statuts, historique
- query_database : analytics, retours, CA, KPIs, historique commandes
  Schéma : products, orders, order_items, returns, analytics
  Règle : toujours anonymiser — utilise customer_id pas customer_name

Règles :
- Toujours utiliser un outil plutôt que ta mémoire
- Pour les questions chiffrées → combine shopify + calculate
- Réponds toujours en français
- Maximum 20 résultats par requête Shopify"""



# ============================================================
# ÉTAT DE L'AGENT
# ============================================================
class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]

# ============================================================
# NŒUDS DU GRAPHE
# ============================================================
def agent_node(state: AgentState):
    """Le cerveau — Claude réfléchit et décide"""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Décide si on continue ou si on arrête"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# ============================================================
# CONSTRUCTION DU GRAPHE
# ============================================================
tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

agent = graph.compile()

# ============================================================
# FONCTIONS PUBLIQUES
# ============================================================
def run_agent(question: str) -> str:
    """Lance l'agent avec une question"""
    result = agent.invoke({
        "messages": [HumanMessage(content=question)]
    })
    return result["messages"][-1].content

def initialize():
    """Initialise les ressources au démarrage"""
    print("🧠 Initialisation de la base vectorielle...")
    init_vectorstore()
    print("✅ Agent prêt !")