import streamlit as st
import src.agent.tools as tools

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from src.config import get_llm_api_key
class StreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.steps = []
    def on_chain_start(self, serialized, inputs, **kwargs):
        self.steps.clear()
    def on_tool_start(self, serialized, input_str, **kwargs):
        self.steps.append(f"▶️ Chamando ferramenta: `{serialized['name']}` com entrada: `{input_str}`")
        self.container.markdown("\n\n".join(self.steps))
    def on_tool_end(self, output, **kwargs):
        self.steps.append(f"✅ Ferramenta retornou: `{output}`")
        self.container.markdown("\n\n".join(self.steps))

st.set_page_config(page_title="SIEAD-SMART | Agente Preditivo", page_icon="🧠", layout="wide")

with st.sidebar:
    st.title("🧠 SIEAD-SMART")
    st.subheader("Agente de IA Preditivo")
    st.markdown("Bem-vindo ao seu assistente inteligente! Este agente usa tecnologia de IA para analisar tendências e padrões nos dados históricos.")
    if st.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Desenvolvido como um projeto de IA de ponta a ponta.")

@st.cache_resource
def load_llm():
    try:
        api_key = get_llm_api_key("GOOGLE")
        if not api_key:
             raise ValueError("Chave de API da Google não encontrada.")
        return ChatGoogleGenerativeAI(
            google_api_key=api_key, 
            model="gemini-1.5-flash", 
            temperature=0
        )
    except Exception as e:
        st.error(f"ERRO ao carregar o modelo de linguagem: {e}")
        st.stop()

llm = load_llm()

functions = [tools.predict_revenue_for_specific_date, tools.summarize_revenue_forecast, tools.predict_revenue_for_tomorrow]
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "Seu nome é Edu e você é um assistente financeiro amigável e prestativo. Use as ferramentas disponíveis para responder às perguntas do usuário."),
    MessagesPlaceholder(variable_name="chat_history", optional=True), ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
agent = create_openai_tools_agent(llm, functions, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=functions, verbose=True)

st.header("💬 Converse com seu Agente Financeiro")
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Olá! Em que posso ajudar hoje?"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("Sua pergunta aqui..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        thinking_container = st.expander("🤔 Raciocínio do Agente...")
        response_container = st.empty()
        
        callback = StreamlitCallbackHandler(thinking_container)
        
        with st.spinner("Analisando e consultando os modelos..."):
            response = agent_executor.invoke(
                {"input": user_prompt, "chat_history": st.session_state.messages[:-1]},
                {"callbacks": [callback]}
            )
            response_container.markdown(response["output"])
            
    st.session_state.messages.append({"role": "assistant", "content": response["output"]})