# main.py

import sys
from PyQt6.QtWidgets import QApplication
# Importa a classe principal da sua interface
from src.interface import SistemaLanchonetePremium

def main():
    """Função principal para iniciar a aplicação."""
    # 1. Cria a instância do QApplication (essencial e deve ser a primeira)
    #    sys.argv permite passar argumentos da linha de comando para o Qt, se necessário.
    app = QApplication(sys.argv)

    # 2. Cria uma instância da sua janela principal (que contém toda a lógica).
    main_window = SistemaLanchonetePremium()

    # 3. Exibe a janela principal.
    #    A própria janela decidirá se mostra o login, as abas ou o PDV.
    main_window.show()
    # Opcional: Se quiser que a janela comece maximizada:
    # main_window.showMaximized()

    # 4. Inicia o loop de eventos do Qt.
    #    A aplicação ficará em execução aqui, processando eventos (cliques, etc.)
    #    até que a janela principal seja fechada.
    #    sys.exit() garante que o código de saída da aplicação seja retornado corretamente.
    sys.exit(app.exec())

# Bloco padrão para executar a função main() quando o script é rodado diretamente.
if __name__ == '__main__':
    main()