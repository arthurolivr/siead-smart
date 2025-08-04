import os
import sys
import subprocess

# Garante que a raiz do projeto está no sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Configura variável de ambiente PYTHONPATH para a raiz
    os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))

    # Chama o streamlit rodando o app no src/ui/streamlit_app.py
    subprocess.run(["streamlit", "run", "src/ui/streamlit_app.py"])

if __name__ == "__main__":
    main()