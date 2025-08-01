import streamlit as st
import sys
from datetime import date, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from config import get_llm_api_key
from agent import tools as agent_tools

print(agent_tools.get_registration_fees("2025-03-31", "FAMART"))  # Example usage to ensure import works
sys.exit(0)  # Exit after the import test to avoid running the Streamlit app
class StreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.steps = []

    def on_chain_start(self, serialized, inputs, **kwargs):
        self.steps.clear()

    def on_tool_start(self, serialized, input_str, **kwargs):
        self.steps.append(
            f"▶️ Chamando ferramenta: `{serialized['name']}` com entrada: `{input_str}`"
        )
        self.container.markdown("\n\n".join(self.steps))

    def on_tool_end(self, output, **kwargs):
        self.steps.append(f"✅ Ferramenta retornou: `{output}`")
        self.container.markdown("\n\n".join(self.steps))


st.set_page_config(page_title="SIEAD-SMART | Agente Preditivo", page_icon="🧠", layout="wide")
with st.sidebar:
    st.title("🧠 SIEAD-SMART")
    st.subheader("Agente de IA Preditivo")
    st.markdown("""
    Bem-vindo ao seu assistente inteligente! Este agente usa tecnologia de IA para analisar tendências e padrões nos dados históricos, permitindo realizar previsões de faturamento para as instituições **Famart** e **IPB**.
    """)
    if st.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Desenvolvido como um projeto de IA de ponta a ponta.")


@st.cache_resource
def load_llm() -> ChatGoogleGenerativeAI:
    api_key = get_llm_api_key("GOOGLE")
    if not api_key:
        raise ValueError("Chave de API da Google não encontrada.")
    return ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model="gemini-1.5-flash",
        temperature=0,
        convert_system_message_to_human=True,
    )

llm = load_llm()

functions = [
    agent_tools.predict_revenue_for_specific_date,
    agent_tools.summarize_revenue_forecast,
    agent_tools.predict_revenue_for_tomorrow,
    agent_tools.get_registration_fees,
]
prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     """Você é Edu, sua tarefa é usar as ferramentas disponíveis para responder às perguntas do usuário.
     As ferramentas exigem um parâmetro 'db_name', que pode ser 'FAMART', 'IPB', ou 'TODOS'.
     Você receberá este parâmetro com base na pergunta do usuário. Use-o sempre.
     Se 'db_name' for 'TODOS', isso significa que o usuário quer uma visão consolidada de ambas as instituições.
     Seja sempre claro, profissional e responda com base nos dados retornados pelas ferramentas."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
agent = create_openai_tools_agent(llm, functions, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=functions, verbose=True)

st.header("💬 Converse com seu Agente Financeiro")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Em que posso ajudar hoje? Você pode perguntar sobre Famart, IPB ou ambos."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def detect_db_name(texto: str) -> str:
    texto_lower = texto.lower()
    if "ipb" in texto_lower:
        return "IPB"
    if "famart" in texto_lower:
        return "FAMART"
    return "TODOS"

if user_prompt := st.chat_input(
    "Ex: 'Qual a previsão para amanhã na Famart?' ou 'E para os próximos 30 dias?'"
):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    with st.chat_message("assistant"):
        thinking_container = st.expander("🤔 Raciocínio do Agente...")
        response_container = st.empty()
        callback = StreamlitCallbackHandler(thinking_container)
        db_context = detect_db_name(user_prompt)
        with st.spinner(f"Analisando dados para: {db_context}..."):
            result = agent_executor.invoke(
                {"input": user_prompt, "chat_history": st.session_state.messages[:-1], "db_name": db_context},
                {"callbacks": [callback]}
            )
            response_container.markdown(result["output"])
    st.session_state.messages.append({"role": "assistant", "content": result["output"]})