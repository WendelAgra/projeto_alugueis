# models.py
import sqlite3

# Função para conectar ao banco de dados
def conectar():
    """Conecta ao banco de dados SQLite e retorna o objeto de conexão."""
    conn = sqlite3.connect('alugueis.db')
    return conn

# Função para criar as tabelas
def criar_tabelas():
    """Cria as tabelas 'casas', 'inquilinos' e 'alugueis' se não existirem."""
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Criar tabela de casas
        # IF NOT EXISTS previne erro caso a tabela já tenha sido criada
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS casas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endereco TEXT NOT NULL,
            valor_aluguel REAL NOT NULL
        )
        ''')

        # Criar tabela de inquilinos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquilinos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL
        )
        ''')

        # Criar tabela de alugueis (relacionamento)
        # FOREIGN KEY estabelece a ligação com as outras tabelas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alugueis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            casa_id INTEGER NOT NULL,
            inquilino_id INTEGER,
            mes_referencia TEXT NOT NULL,
            pago INTEGER NOT NULL DEFAULT 0,  -- 0 para pendente, 1 para pago
            FOREIGN KEY (casa_id) REFERENCES casas (id),
            FOREIGN KEY (inquilino_id) REFERENCES inquilinos (id)
        )
        ''')

        conn.commit()
        print("Tabelas criadas com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        if conn:
            conn.close()

# Bloco que permite executar este script diretamente para criar o banco
if __name__ == '__main__':
    criar_tabelas()