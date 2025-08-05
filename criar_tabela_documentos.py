# criar_tabela_documentos.py
import sqlite3

def criar_tabela():
    conn = None
    try:
        conn = sqlite3.connect('alugueis.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluguel_id INTEGER NOT NULL,
            nome_original TEXT NOT NULL,
            nome_seguro TEXT NOT NULL,
            FOREIGN KEY (aluguel_id) REFERENCES alugueis (id)
        )
        ''')
        print("Tabela 'documentos' verificada/criada com sucesso!")
        conn.commit()

    except sqlite3.Error as e:
        print(f"Erro ao criar a tabela de documentos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    criar_tabela()