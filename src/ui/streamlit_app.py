# Python Standard Library
from typing import Callable, Any                   # <-- Adicionado 'Any'

# Third-Party Libraries
import streamlit as st
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from streamlit.delta_generator import DeltaGenerator # <-- Adicionado 'DeltaGenerator'

# Local Application Imports
import src.agent.tools as agent_tools
from src.config.llm_config import get_llm_api_key


# Carregar a chave da API
ai_current = "GOOGLE"
api_key = get_llm_api_key(ai_current)


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


st.set_page_config(page_title="SIEAD-SMART | Análise Comercial", page_icon="🧠", layout="wide")

with st.sidebar:
    st.title("🧠 SIEAD-SMART")
    st.subheader("Agente de Análise Comercial")
    st.markdown("""Bem-vindo ao seu assistente de negócios inteligente! 
    Este agente usa IA para se conectar em tempo real ao banco de dados e responder perguntas sobre o desempenho comercial, como matrículas, vendas por equipe e performance de agenciadores para as instituições **Famart** e **IPB**.""")
    if st.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Desenvolvido como um projeto de IA de ponta a ponta.")


@st.cache_resource
def load_llm():
    """
    Carrega o modelo de linguagem. Agora com suporte ao DeepSeek e os parâmetros corretos.
    """
    if not api_key:
        raise ValueError(f"Chave de API para o provedor {ai_current} não encontrada.")

    if ai_current == "GOOGLE":
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model="gemini-2.5-flash-lite",
            temperature=0,
            convert_system_message_to_human=True,
        )
    
    if ai_current == "DEEPSEEK":
        return ChatOpenAI(
            model="deepseek-chat",
            temperature=0,
            api_key=SecretStr(api_key),
            base_url="https://api.deepseek.com/v1"
        )
    
    raise ValueError(f"Provedor de LLM desconhecido ou não configurado: {ai_current}")


llm = load_llm()

functions: list[Callable] = [
    agent_tools.get_commercial_analysis,
]

prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     """Você é Edu, um analista de dados sênior. Sua única ferramenta é 'get_commercial_analysis'.

     REGRAS DE COMPORTAMENTO CRÍTICAS:
     1.  **FOCO TOTAL:** Pense passo a passo. Foque **APENAS** na pergunta mais recente do usuário (`human`). Ignore completamente as chamadas de ferramenta antigas no histórico. Sua tarefa é formular **UMA ÚNICA** chamada de ferramenta para responder à pergunta atual.
     2.  **Analise a Pergunta:** Leia a pergunta do usuário para determinar o `analysis_type` correto ('summary', 'team_performance', 'agent_performance', 'payment_breakdown').
     3.  **Datas:** Converta QUALQUER expressão de data do usuário para um formato de string claro. Ex: 'primeira semana de março de 2025' -> 'de 2025-03-01 a 2025-03-07'.
     4.  **Instituição Padrão:** Se o usuário não especificar 'Famart' ou 'IPB', use `db_name='TODOS'`. NUNCA pergunte.
     5.  **Execute e Responda:** Chame a ferramenta e apresente o resultado. Se a ferramenta retornar "Nenhum dado encontrado", informe isso claramente ao usuário.
     """),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
agent: Runnable = create_openai_tools_agent(llm, functions, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=functions, verbose=True)


def detect_db_name(texto: str) -> str:
    texto_lower: str = texto.lower()
    if "ipb" in texto_lower:
        return "IPB"
    if "famart" in texto_lower:
        return "FAMART"
    return "TODOS"


# Interface do Streamlit
st.header("💬 Converse com seu Agente de Análise Comercial")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Olá! Sou o Edu. Como posso ajudar com a análise comercial hoje? Posso analisar matrículas, vendas por equipe e performance de agenciadores."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input(
        "Ex: 'Qual o total de matrículas da equipe Gold ontem na Famart?' ou 'Como foi o desempenho das equipes no último mês?'"
):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    with st.chat_message("assistant"):
        thinking_container: DeltaGenerator = st.expander("🤔 Raciocínio do Agente...")
        response_container: DeltaGenerator = st.empty()
        callback = StreamlitCallbackHandler(thinking_container)
        db_context: str = detect_db_name(user_prompt)
        with st.spinner(f"Analisando dados para: {db_context}..."):
            result: dict[str, Any] = agent_executor.invoke(
                {"input": user_prompt, "chat_history": st.session_state.messages[:-1], "db_name": db_context},
                {"callbacks": [callback]}
            )
            response_container.markdown(result["output"])
    st.session_state.messages.append({"role": "assistant", "content": result["output"]})