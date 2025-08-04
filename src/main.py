from src.ia.ia_core import IA

def main():
    ia = IA()
    question = "Quantos usuários temos?"
    response = ia.ask(question, "example")
    print(f"Resposta da IA: {response}")

if __name__ == "__main__":
    main()