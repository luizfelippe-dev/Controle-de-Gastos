import sqlite3

# Função para criar a tabela se ela ainda não existir
def create_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    # Criação da tabela com novas colunas: type e is_paid
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value REAL NOT NULL,
            payment_date TEXT,
            type TEXT NOT NULL,  -- 'gain' ou 'expense'
            is_paid INTEGER DEFAULT 0  -- 0 para não pago, 1 para pago
        )
    ''')
    conn.commit()
    print("Tabela expenses criada ou já existente.")
    conn.close()

# Função para adicionar uma despesa/ganho
def add_expense(name, value, payment_date):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO expenses (name, value, payment_date, type) VALUES (?, ?, ?, ?)', (name, value, payment_date, 'expense'))
    conn.commit()
    conn.close()

def add_gain(name, value):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO expenses (name, value, payment_date, type) VALUES (?, ?, ?, ?)', (name, value, None, 'gain'))
    conn.commit()
    conn.close()


# Função para buscar todas as despesas/ganhos
def get_all_expenses():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()

    conn.close()
    return expenses

# Função para editar uma despesa/ganho
def edit_expense(expense_id, new_name, new_value, new_payment_date):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE expenses
        SET name = ?, value = ?, payment_date = ?
        WHERE id = ?
    ''', (new_name, new_value, new_payment_date, expense_id))
    conn.commit()
    conn.close()

# Função para remover uma despesa/ganho
def remove_expense(expense_id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()

    def add_recurring_expense(name, value, day_of_month):
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO expenses (name, value, payment_date, type, is_recurring) VALUES (?, ?, ?, ?, 1)', (name, value, day_of_month, 'expense'))
        conn.commit()
        conn.close()

    def mark_as_paid(expense_id):
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        cursor.execute('UPDATE expenses SET is_paid = 1 WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()

    def mark_as_paid(expense_id):
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        # Atualizar a despesa para marcar como paga
        cursor.execute('UPDATE expenses SET is_paid = 1 WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()



