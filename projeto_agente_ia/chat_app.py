# chat_app.py (Versão para GEMINI)

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import tool, AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import date, timedelta
from tools import prever_faturamento_diario, resumir_previsao_longo_prazo

st.set_page_config(page_title="Agente Financeiro (Gemini)", page_icon="✨")
st.title("🤖 Agente Financeiro Conversacional (Powered by Gemini)")
st.caption("Inteligência por Google Gemini. Tente 'qual a previsão para amanhã?'")

try:
    google_api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("ERRO: Chave de API da Google não encontrada. Crie .streamlit/secrets.toml e adicione sua GOOGLE_API_KEY.")
    st.stop()

@tool
def prever_faturamento_data_especifica(data: str) -> str:
    """Use esta ferramenta para prever o faturamento de um único dia específico. A data DEVE ser uma string no formato 'AAAA-MM-DD'."""
    return prever_faturamento_diario(data)

@tool
def resumir_previsao_periodo(dias: int) -> str:
    """Use esta ferramenta para obter um resumo da previsão de faturamento para um período futuro em dias. Use-a quando o usuário perguntar sobre 'próximos X dias', 'próximo mês' (use 30 dias), etc."""
    return resumir_previsao_longo_prazo(dias)

@tool
def prever_faturamento_amanha() -> str:
    """Use esta ferramenta quando o usuário perguntar especificamente sobre a previsão de 'amanhã'."""
    data_amanha = date.today() + timedelta(days=1)
    return prever_faturamento_diario(data_amanha.strftime('%Y-%m-%d'))

tools = [prever_faturamento_data_especifica, resumir_previsao_periodo, prever_faturamento_amanha]

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente financeiro amigável e prestativo. Use as ferramentas disponíveis para responder às perguntas do usuário."),
    MessagesPlaceholder(variable_name="chat_history", optional=True), ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

llm = ChatGoogleGenerativeAI(google_api_key=google_api_key, model="gemini-1.5-flash", temperature=0, convert_system_message_to_human=True)
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Em que posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando com Gemini..."):
            response = agent_executor.invoke({"input": prompt, "chat_history": st.session_state.messages})
            st.markdown(response["output"])
    st.session_state.messages.append({"role": "assistant", "content": response["output"]})