# criar_tabela_config.py
import sqlite3

def criar_tabela():
    conn = None
    try:
        conn = sqlite3.connect('alugueis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL UNIQUE,
            dia_vencimento_padrao INTEGER DEFAULT 10,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
        ''')
        print("Tabela 'configuracoes' verificada/criada com sucesso!")
        conn.commit()

    except sqlite3.Error as e:
        print(f"Erro ao criar a tabela de configurações: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    criar_tabela()