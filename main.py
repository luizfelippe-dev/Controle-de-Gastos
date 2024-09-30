import sys
from PyQt5.QtWidgets import QApplication
from ui_main import MainUI

def main():
    print("Iniciando a aplicação...")  # Mensagem de depuração
    app = QApplication(sys.argv)

    # Inicializa a interface principal
    window = MainUI()
    window.show()  # Isso é necessário para exibir a janela
    print("Janela principal exibida.")  # Mensagem de depuração

    sys.exit(app.exec_())  # Garante que a aplicação continua executando

if __name__ == '__main__':
    main()
