from datetime import date, timedelta
from src.repositories.venda_repository import VendaRepository
from src.utils.logger import get_logger
import pprint

# Configura o logger e o pretty-printer para uma saída mais legível
logger = get_logger("deploy")
pp = pprint.PrettyPrinter(indent=4)

# --- CONFIGURAÇÕES DO TESTE ---
# Define o intervalo de datas para a busca de dados.
# Aqui, estamos olhando para os últimos 90 dias a partir de hoje.
DATA_INICIO = date.today() - timedelta(days=90)
DATA_FIM = date.today()


# --- FUNÇÃO AUXILIAR PARA BUSCAR DADOS DE TESTE DINAMICAMENTE ---
def get_dynamic_test_data(repo: VendaRepository, db_name: str):
    """
    Busca no banco de dados um exemplo real de venda que tenha equipe e agenciador associados
    para usar nos testes de filtro, tornando o teste robusto e independente de dados fixos.
    """
    print(f"\nBuscando dados de teste dinâmicos no banco '{db_name}'...")

    # Query para encontrar a primeira venda no período que tenha equipe e agenciador válidos
    query = f"""
        SELECT 
            e.nome AS nome_equipe,
            a.nome AS nome_agenciador
        FROM {db_name}.venda v
        JOIN {db_name}.agenciador a ON a.usuario_id = v.vendedor_id
        JOIN {db_name}.equipe_usuario eu ON eu.usuario_id = v.vendedor_id
        JOIN {db_name}.equipe e ON e.id = eu.equipe_id
        WHERE v.data_venda BETWEEN %(start_date)s AND %(end_date)s
          AND e.nome IS NOT NULL
          AND a.nome IS NOT NULL
        LIMIT 1
    """
    params = {'start_date': DATA_INICIO, 'end_date': DATA_FIM}

    try:
        result = repo.execute_query(query, params)
        if result:
            print(">>> Dados de teste encontrados com sucesso! <<<")
            return result[0]['nome_equipe'], result[0]['nome_agenciador']
    except Exception as e:
        logger.error(f"Erro ao buscar dados dinâmicos em {db_name}: {e}")

    print(
        ">>> ATENÇÃO: Não foram encontrados dados de teste válidos no período. Os testes de filtro serão pulados. <<<")
    return None, None


# --- INÍCIO DA EXECUÇÃO DOS TESTES DE REPOSITÓRIO ---
logger.info(">>> INÍCIO DA EXECUÇÃO DOS TESTES DE REPOSITÓRIO <<<")

try:
    # Cria a instância do repositório que vamos testar
    repo = VendaRepository()

    # Pega dinamicamente um nome de equipe e agenciador de um dos bancos
    # Mude para "ipb" se quiser pegar os dados de teste de lá
    db_para_buscar_dados = "famart"
    NOME_EQUIPE_TESTE, NOME_AGENCIADOR_TESTE = get_dynamic_test_data(repo, db_para_buscar_dados)

    # --- Teste 1: Consulta geral (sem filtros) ---
    print("\n--- TESTE 1: Buscando matrículas para 'TODOS' (sem filtros)... ---")
    resultado_geral = repo.fetch_enrollments(
        date_start=DATA_INICIO,
        date_end=DATA_FIM,
        db_name="TODOS"
    )
    print(f"Encontrados {len(resultado_geral)} registros.")
    if resultado_geral:
        print("Amostra dos dados (3 primeiros registros):")
        pp.pprint(resultado_geral[:3])

    # --- Teste 2: Consulta com filtro de EQUIPE (só executa se encontrou uma equipe válida) ---
    if NOME_EQUIPE_TESTE:
        print(f"\n--- TESTE 2: Filtrando pela equipe encontrada dinamicamente: '{NOME_EQUIPE_TESTE}'... ---")
        resultado_equipe = repo.fetch_enrollments(
            date_start=DATA_INICIO,
            date_end=DATA_FIM,
            db_name="TODOS",
            team_name=NOME_EQUIPE_TESTE
        )
        print(f"Encontrados {len(resultado_equipe)} registros para a equipe.")
        if resultado_equipe:
            pp.pprint(resultado_equipe[:3])
    else:
        print("\n--- TESTE 2: Ignorado (nenhuma equipe válida para teste foi encontrada no período). ---")

    # --- Teste 3: Consulta com filtro de AGENCIADOR (só executa se encontrou um agenciador válido) ---
    if NOME_AGENCIADOR_TESTE:
        print(f"\n--- TESTE 3: Filtrando pelo agenciador encontrado dinamicamente: '{NOME_AGENCIADOR_TESTE}'... ---")
        resultado_agenciador = repo.fetch_enrollments(
            date_start=DATA_INICIO,
            date_end=DATA_FIM,
            db_name="TODOS",
            agent_name=NOME_AGENCIADOR_TESTE
        )
        print(f"Encontrados {len(resultado_agenciador)} registros para o agenciador.")
        if resultado_agenciador:
            pp.pprint(resultado_agenciador[:3])
    else:
        print("\n--- TESTE 3: Ignorado (nenhum agenciador válido para teste foi encontrado no período). ---")

except Exception as e:
    logger.error(f"Ocorreu um erro fatal durante os testes: {e}")
    print(f"\nERRO: {e}")