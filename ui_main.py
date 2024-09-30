from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout, QDateEdit, QMessageBox
from PyQt5.QtCore import Qt
from database import create_db, add_expense, add_gain, get_all_expenses, mark_as_paid, remove_expense, edit_expense
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

        # Campo para a data de pagamento/recebimento
        self.date_label = QLabel('Data de Pagamento/Recebimento (dd-mm-aaaa):')
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

        # Tabela para visualizar ganhos
        self.gain_table = QTableWidget()
        self.gain_table.setColumnCount(4)  # Quatro colunas: ID, Nome, Valor, Data
        self.gain_table.setHorizontalHeaderLabels(['ID', 'Nome', 'Valor', 'Data'])
        self.gain_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.gain_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Impedir edição direta
        self.gain_table.setDragEnabled(True)  # Habilitar arraste
        self.gain_table.viewport().setAcceptDrops(True)
        self.gain_table.setDropIndicatorShown(True)
        self.gain_table.setDragDropOverwriteMode(False)  # Evitar sobrescrita de linhas
        self.gain_table.dropEvent = self.drop_event_handler  # Adicionar o handler de drop
        main_layout.addWidget(QLabel('Ganhos:'))
        main_layout.addWidget(self.gain_table)

        # Tabela para visualizar despesas
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(4)  # Quatro colunas: ID, Nome, Valor, Data
        self.expense_table.setHorizontalHeaderLabels(['ID', 'Nome', 'Valor', 'Data'])
        self.expense_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.expense_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Impedir edição direta
        self.expense_table.setDragEnabled(True)  # Habilitar arraste
        self.expense_table.viewport().setAcceptDrops(True)
        self.expense_table.setDropIndicatorShown(True)
        self.expense_table.setDragDropOverwriteMode(False)  # Evitar sobrescrita de linhas
        self.expense_table.dropEvent = self.drop_event_handler  # Adicionar o handler de drop
        main_layout.addWidget(QLabel('Despesas:'))
        main_layout.addWidget(self.expense_table)

        # Adicionar os botões de "Editar" e "Remover"
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

        # Adicionar seleção de mês e ano
        self.month_label = QLabel('Selecione o Mês:')
        self.month_combo = QComboBox()
        self.month_combo.addItems(['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])
        main_layout.addWidget(self.month_label)
        main_layout.addWidget(self.month_combo)

        # Definir a variável current_date
        current_date = datetime.now()

        self.year_label = QLabel('Selecione o Ano:')
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(year) for year in range(current_date.year, current_date.year - 10, -1)])  # Anos recentes
        main_layout.addWidget(self.year_label)
        main_layout.addWidget(self.year_combo)

        # Adicionar seleção do período (Mensal/Anual)
        self.period_label = QLabel('Selecione o Período:')
        self.period_combo = QComboBox()
        self.period_combo.addItems(['Mensal', 'Anual'])
        main_layout.addWidget(self.period_label)
        main_layout.addWidget(self.period_combo)

        # Botão para mostrar o resumo
        self.summary_button = QPushButton('Resumo')
        main_layout.addWidget(self.summary_button)
        self.summary_button.clicked.connect(self.show_summary)

        # Define o layout da janela principal
        self.setLayout(main_layout)

        # Carrega os dados existentes na tabela e atualiza o saldo
        self.load_expenses()
        self.update_balance()
    
    def add_gain(self):
        name = self.name_input.text()
        value = self.value_input.text()
        payment_date = self.date_input.text()  # Adicionando a data de ganho

        if not name or not value or not payment_date:
            print("Por favor, preencha todos os campos.")
            return

        try:
            value = float(value)
            # Tenta converter a data para garantir que ela está no formato correto
            datetime.strptime(payment_date, '%d-%m-%Y')
            add_gain(name, value, payment_date)  # Passando a data para a função do banco de dados
            self.name_input.clear()
            self.value_input.clear()
            self.date_input.clear()
            self.load_expenses()
            self.update_balance()
            print(f"Ganho '{name}' de valor {value} adicionado com sucesso.")
        except ValueError:
            print("Por favor, insira um valor numérico e uma data válida.")

    
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
        # Limpa as tabelas antes de carregar os dados
        self.gain_table.setRowCount(0)
        self.expense_table.setRowCount(0)

        # Obtém todos os registros do banco de dados
        expenses = get_all_expenses()
        for expense in expenses:
            # Verificar se é ganho ou despesa
            if expense[4] == 'gain':
                table = self.gain_table
            else:
                table = self.expense_table

            # Adicionar os dados à tabela correta
            row_number = table.rowCount()
            table.insertRow(row_number)
            table.setItem(row_number, 0, QTableWidgetItem(str(expense[0])))  # ID
            table.setItem(row_number, 1, QTableWidgetItem(expense[1]))  # Nome
            table.setItem(row_number, 2, QTableWidgetItem(f"{expense[2]:.2f}"))  # Valor
            table.setItem(row_number, 3, QTableWidgetItem(expense[3] if expense[3] else 'N/A'))  # Data

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
        # Verificar se há uma linha selecionada na tabela de despesas
        selected_row = self.expense_table.currentRow()
        if selected_row >= 0:  # Verifica se alguma linha está selecionada
            expense_id = self.expense_table.item(selected_row, 0)
            if expense_id is not None:  # Certificar-se de que o item não é None
                try:
                    expense_id = int(expense_id.text())
                    remove_expense(expense_id)
                    self.load_expenses()
                    self.update_balance()
                    print(f"Despesa removida com sucesso.")
                except Exception as e:
                    self.show_message(f"Erro ao remover a despesa: {e}")
            return

        # Verificar se há uma linha selecionada na tabela de ganhos
        selected_row = self.gain_table.currentRow()
        if selected_row >= 0:  # Verifica se alguma linha está selecionada
            gain_id = self.gain_table.item(selected_row, 0)
            if gain_id is not None:  # Certificar-se de que o item não é None
                try:
                    gain_id = int(gain_id.text())
                    remove_expense(gain_id)
                    self.load_expenses()
                    self.update_balance()
                    print(f"Ganho removido com sucesso.")
                except Exception as e:
                    self.show_message(f"Erro ao remover o ganho: {e}")
            return

        # Se nenhuma linha estiver selecionada em ambas as tabelas, mostrar uma mensagem
        self.show_message("Por favor, selecione um item para remover.")


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
        
        # Adicionar seleção de mês e ano apenas para o período mensal
        if period == 'Mensal':
            month = self.month_combo.currentIndex() + 1  # Índices do ComboBox começam em 0, então adicionar 1
            year = int(self.year_combo.currentText())
        elif period == 'Anual':
            year = current_date.year  # Para o período anual, usamos o ano atual

        for expense in expenses:
            # Ignorar se a data de pagamento for None
            if not expense[3]:
                continue

            try:
                expense_date = datetime.strptime(expense[3], '%d-%m-%Y')

                if period == 'Mensal':
                    # Verificar se o registro corresponde ao mês e ano selecionados
                    if expense_date.year == year and expense_date.month == month:
                        expense_summary[expense[1]] += expense[2]

                elif period == 'Anual':
                    if expense_date.year == year:
                        expense_summary[expense[1]] += expense[2]

            except ValueError:
                self.show_message(f"Data inválida encontrada para a despesa: {expense[1]}")

        labels = list(expense_summary.keys())
        values = list(expense_summary.values())

        if not labels:
            self.show_message(f"Nenhuma despesa encontrada para o período {period}.")
            return

        plt.figure(figsize=(8, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        if period == 'Mensal':
            plt.title(f'Resumo de Despesas para {self.month_combo.currentText()} de {year}')
        elif period == 'Anual':
            plt.title(f'Resumo Anual de Despesas para {year}')
        plt.show()

    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle('Informação')
        msg_box.exec_()

    def drop_event_handler(self, event):
        # Obtém a tabela de origem e destino
        source = event.source()
        target_row = source.rowAt(event.pos().y())

        if source == self.gain_table:
            selected_row = self.gain_table.currentRow()
        elif source == self.expense_table:
            selected_row = self.expense_table.currentRow()
        else:
            return

        if selected_row < 0 or target_row < 0 or selected_row == target_row:
            # Se nenhuma linha estiver selecionada ou não for um movimento válido, cancelar
            return

        # Trocar os itens da linha selecionada com os da linha alvo
        self.swap_table_rows(source, selected_row, target_row)

    def swap_table_rows(self, table, row1, row2):
        # Armazena os dados da linha 1
        row_data = []
        for column in range(table.columnCount()):
            item = table.item(row1, column)
            row_data.append(QTableWidgetItem(item.text()) if item else None)

        # Move os dados da linha 2 para a linha 1
        for column in range(table.columnCount()):
            item = table.item(row2, column)
            table.setItem(row1, column, QTableWidgetItem(item.text()) if item else None)

        # Move os dados da linha 1 (armazenados) para a linha 2
        for column, item in enumerate(row_data):
            table.setItem(row2, column, QTableWidgetItem(item.text()) if item else None)
