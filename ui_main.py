from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout, QDateEdit
from database import create_db, add_expense, add_gain, get_all_expenses, remove_expense, edit_expense
from plyer import notification
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

class MainUI(QWidget):
    def __init__(self):
        super().__init__()

        # Carregar estilo do arquivo QSS
        with open("style.qss", "r") as style_file:
            self.setStyleSheet(style_file.read())

        # Criação do banco de dados
        create_db()

        # Layout principal
        main_layout = QVBoxLayout()

        # Exibir saldo atual
        self.balance_label = QLabel('Saldo Atual: R$ 0.00')
        main_layout.addWidget(self.balance_label)

        # Grid layout para os campos de entrada
        form_layout = QHBoxLayout()
        form_layout.setSpacing(10)

        # Campo para o nome da despesa/ganho
        self.name_label = QLabel('Nome da Despesa/Ganho:')
        self.name_input = QLineEdit()
        form_layout.addWidget(self.name_label)
        form_layout.addWidget(self.name_input)

        # Campo para o valor da despesa/ganho
        self.value_label = QLabel('Valor:')
        self.value_input = QLineEdit()
        form_layout.addWidget(self.value_label)
        form_layout.addWidget(self.value_input)

        # Campo para a data de pagamento (apenas para despesas)
        self.date_label = QLabel('Data de Pagamento (dd-mm-aaaa):')
        self.date_input = QLineEdit()
        form_layout.addWidget(self.date_label)
        form_layout.addWidget(self.date_input)

        # Adicionar form_layout ao layout principal
        main_layout.addLayout(form_layout)

        # Botões para adicionar ganho e despesa
        button_layout = QHBoxLayout()
        self.add_gain_button = QPushButton('Adicionar Ganho')
        self.add_expense_button = QPushButton('Adicionar Despesa')
        button_layout.addWidget(self.add_gain_button)
        button_layout.addWidget(self.add_expense_button)

        # Conectar os botões aos métodos
        self.add_gain_button.clicked.connect(self.add_gain)
        self.add_expense_button.clicked.connect(self.add_expense)

        # Adicionar button_layout ao layout principal
        main_layout.addLayout(button_layout)

        # Tabela para visualizar despesas/ganhos
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(4)  # Quatro colunas: ID, Nome, Valor, Data
        self.expense_table.setHorizontalHeaderLabels(['ID', 'Nome', 'Valor', 'Data'])
        main_layout.addWidget(self.expense_table)

        # Botões para editar e remover despesas
        edit_remove_layout = QHBoxLayout()
        self.edit_button = QPushButton('Editar Despesa')
        self.remove_button = QPushButton('Remover Despesa')
        edit_remove_layout.addWidget(self.edit_button)
        edit_remove_layout.addWidget(self.remove_button)

        # Conectar os botões aos métodos
        self.edit_button.clicked.connect(self.edit_expense)
        self.remove_button.clicked.connect(self.remove_expense)

        # Adicionar edit_remove_layout ao layout principal
        main_layout.addLayout(edit_remove_layout)

        # Define o layout da janela principal
        self.setLayout(main_layout)

        # Carrega os dados existentes na tabela e atualiza o saldo
        self.load_expenses()
        self.update_balance()
    
    def add_gain(self):
        name = self.name_input.text()
        value = self.value_input.text()

        if not name or not value:
            print("Por favor, preencha todos os campos.")
            return

        try:
            value = float(value)
            add_gain(name, value)
            self.name_input.clear()
            self.value_input.clear()
            self.load_expenses()
            self.update_balance()
            print(f"Ganho '{name}' de valor {value} adicionado com sucesso.")
        except ValueError:
            print("Por favor, insira um valor numérico válido.")
    
    def add_expense(self):
        name = self.name_input.text()
        value = self.value_input.text()
        payment_date = self.date_input.text()

        if not name or not value or not payment_date:
            print("Por favor, preencha todos os campos.")
            return

        try:
            value = float(value)
            add_expense(name, value, payment_date)
            self.name_input.clear()
            self.value_input.clear()
            self.date_input.clear()
            self.load_expenses()
            self.update_balance()
            print(f"Despesa '{name}' de valor {value} adicionada com sucesso.")
        except ValueError:
            print("Por favor, insira um valor numérico válido.")
    
    def update_balance(self):
        expenses = get_all_expenses()
        balance = sum(expense[2] if expense[4] == 'gain' else -expense[2] for expense in expenses)
        self.balance_label.setText(f'Saldo Atual: R$ {balance:.2f}')

    def load_expenses(self):
        # Limpa a tabela antes de carregar os dados
        self.expense_table.setRowCount(0)

        # Obtém todos os registros do banco de dados
        expenses = get_all_expenses()
        for row_number, expense in enumerate(expenses):
            self.expense_table.insertRow(row_number)
            self.expense_table.setItem(row_number, 0, QTableWidgetItem(str(expense[0])))  # ID
            self.expense_table.setItem(row_number, 1, QTableWidgetItem(expense[1]))  # Nome
            self.expense_table.setItem(row_number, 2, QTableWidgetItem(f"{expense[2]:.2f}"))  # Valor
            self.expense_table.setItem(row_number, 3, QTableWidgetItem(expense[3] if expense[3] else 'N/A'))  # Data

    def edit_expense(self):
        selected_row = self.expense_table.currentRow()
        if selected_row < 0:
            print("Por favor, selecione uma despesa para editar.")
            return

        expense_id = int(self.expense_table.item(selected_row, 0).text())
        new_name = self.name_input.text()
        new_value = self.value_input.text()
        new_payment_date = self.date_input.text()

        if not new_name or not new_value or not new_payment_date:
            print("Por favor, preencha todos os campos.")
            return

        try:
            new_value = float(new_value)
            edit_expense(expense_id, new_name, new_value, new_payment_date)
            self.load_expenses()
            self.update_balance()
            print(f"Despesa '{new_name}' editada com sucesso.")
        except ValueError:
            print("Por favor, insira um valor numérico válido ou data válida.")
        except Exception as e:
            print(f"Erro ao editar a despesa: {e}")

    def remove_expense(self):
        selected_row = self.expense_table.currentRow()
        if selected_row < 0:
            print("Por favor, selecione uma despesa para remover.")
            return

        expense_id = int(self.expense_table.item(selected_row, 0).text())
        try:
            remove_expense(expense_id)
            self.load_expenses()
            self.update_balance()
            print(f"Despesa removida com sucesso.")
        except Exception as e:
            print(f"Erro ao remover a despesa: {e}")

    def check_upcoming_payments(self):
        expenses = get_all_expenses()
        current_date = datetime.now()

        for expense in expenses:
            try:
                payment_date = datetime.strptime(expense[3], '%d-%m-%Y')
                days_until_payment = (payment_date - current_date).days

                if 0 <= days_until_payment <= 3:
                    notification.notify(
                        title="Lembrete de Pagamento",
                        message=f"Lembre-se do pagamento: {expense[1]} no valor de {expense[2]:.2f}",
                        timeout=5
                    )
            except ValueError:
                print(f"Data inválida encontrada para a despesa: {expense[1]}")

    def show_summary(self):
        period = self.period_combo.currentText()
        expenses = get_all_expenses()
        expense_summary = defaultdict(float)
        current_date = datetime.now()

        for expense in expenses:
            expense_date = datetime.strptime(expense[3], '%d-%m-%Y')

            if period == 'Mensal':
                if expense_date.year == current_date.year and expense_date.month == current_date.month:
                    expense_summary[expense[1]] += expense[2]

            elif period == 'Anual':
                if expense_date.year == current_date.year:
                    expense_summary[expense[1]] += expense[2]

            else:
                start_date = self.start_date_edit.date().toPyDate()
                end_date = self.end_date_edit.date().toPyDate()
                if start_date <= expense_date <= end_date:
                    expense_summary[expense[1]] += expense[2]

        labels = list(expense_summary.keys())
        values = list(expense_summary.values())

        if not labels:
            print(f"Nenhuma despesa encontrada para o período {period}.")
            return

        plt.figure(figsize=(8, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(f'Resumo {period} de Despesas/Ganhos')
        plt.show()
