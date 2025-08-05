import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler

from src.config.llm_config import get_llm_api_key
import src.agent.tools as agent_tools

ai_current = "AIMLAPI"
api_key = get_llm_api_key(ai_current)

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

# Organize o layout Streamlit (copie do seu código, é ótimo)
st.set_page_config(page_title="SIEAD-SMART | Agente Preditivo", page_icon="🧠", layout="wide")
with st.sidebar:
    st.title("🧠 SIEAD-SMART")
    st.subheader("Agente de IA Preditivo")
    st.markdown("""Bem-vindo ao seu assistente inteligente! Este agente usa tecnologia de IA para analisar tendências e padrões nos dados históricos, permitindo realizar previsões de faturamento para as instituições **Famart** e **IPB**.""")
    if st.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.messages = []
        st.experimental_rerun()
    st.caption("Desenvolvido como um projeto de IA de ponta a ponta.")


# Inicialize o modelo LLM com cache
@st.cache_resource
def load_llm():
    if not api_key:
        raise ValueError("Chave de API da Google não encontrada.")

    if ai_current == "GOOGLE":
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model="gemini-1.5-flash",
            temperature=0,
            convert_system_message_to_human=True,
        )

    if ai_current == "OPENROUTER":
        return ChatOpenAI(
            model="gpt-4",  # ou "gpt-3.5-turbo"
            temperature=0,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )

    if ai_current == "AIMLAPI":
        return ChatOpenAI(
            model="meta-llama/Llama-Vision-Free",  # ou "gpt-3.5-turbo"
            temperature=0,
            openai_api_key=api_key,
            openai_api_base="https://api.aimlapi.com/v1"
        )

    return None


llm = load_llm()

#definindo as funções
functions = [
    agent_tools.get_registration_fees,
]

#Crie o prompt e o agente LangChain
prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     """Você é Edu, sua tarefa é usar as ferramentas disponíveis para responder às perguntas do usuário.
     As ferramentas exigem um parâmetro 'db_name', que pode ser 'FAMART', 'IPB', ou 'TODOS'.
     Você receberá este parâmetro com base na pergunta do usuário. Use-o sempre.
     As ferramentas retornam textos já formatados com os dados.
     Seja sempre claro, profissional e responda com base nos dados retornados pelas ferramentas.
     **use as ferramentas disponíveis** para responder. Não invente dados.
     As ferramentas acessam os dados reais.
     """),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(llm, functions, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=functions, verbose=True)

#Função auxiliar para detectar banco (Famart, IPB ou ambos)
def detect_db_name(texto: str) -> str:
    texto_lower = texto.lower()
    if "ipb" in texto_lower:
        return "IPB"
    if "famart" in texto_lower:
        return "FAMART"
    return "TODOS"

#Fluxo principal do chat

st.header("💬 Converse com seu Agente Financeiro")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Em que posso ajudar hoje? Você pode perguntar sobre Famart, IPB ou ambos."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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