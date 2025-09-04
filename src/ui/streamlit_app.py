import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler

from src.config.llm_config import get_llm_api_key
import src.agent.tools as agent_tools

ai_current = "GOOGLE"
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
    if not api_key:
        raise ValueError("Chave de API da Google não encontrada.")

    if ai_current == "GOOGLE":
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model="gemini-1.5-flash",
            temperature=0,
            convert_system_message_to_human=True,
        )

llm = load_llm()

functions = [
    agent_tools.analyze_enrollments,
]

prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     """Você é Edu, um analista de dados sênior e especialista em usar a ferramenta 'analyze_enrollments'. Siga estas regras rigorosamente:

     REGRAS DE COMPORTAMENTO:
     1.  **Instituição Padrão:** Se o usuário NÃO especificar 'Famart' ou 'IPB', o sistema definirá `db_name` como 'TODOS'. VOCÊ DEVE USAR 'TODOS' DIRETAMENTE. **NUNCA, EM HIPÓTESE ALGUMA, peça ao usuário para escolher.**
     2.  **Datas:** Antes de chamar a ferramenta, converta expressões como 'mês passado', 'última semana', 'primeira quinzena de março' para um formato de intervalo explícito, como 'de A a B'. Por exemplo, 'mês passado' (estamos em Setembro de 2025) deve ser convertido para `date_str='de 2025-08-01 a 2025-08-31'`.
     3.  **Uso dos Parâmetros:** A ferramenta `analyze_enrollments` é sua única fonte de dados. Confie na sua documentação.
         - Se o usuário pedir detalhes de pagamento, **VOCÊ DEVE** chamar a ferramenta com `detailed=True`.
         - Se o usuário mencionar uma equipe ou agenciador, **VOCÊ DEVE** usar os parâmetros `team` ou `agent`.
     4.  **Seja Direto:** Responda à pergunta do usuário com os dados da ferramenta. Não faça perguntas desnecessárias se a informação já foi fornecida ou pode ser inferida.
     """),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(llm, functions, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=functions, verbose=True)

def detect_db_name(texto: str) -> str:
    texto_lower = texto.lower()
    if "ipb" in texto_lower:
        return "IPB"
    if "famart" in texto_lower:
        return "FAMART"
    return "TODOS"

st.header("💬 Converse com seu Agente de Análise")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o Edu. Como posso ajudar com a análise de matrículas hoje?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input(
    "Ex: 'Qual o total de matrículas da equipe Gold ontem na Famart?'"
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