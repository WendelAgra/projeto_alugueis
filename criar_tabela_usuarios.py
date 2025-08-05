# criar_tabela_usuarios.py
import sqlite3

def criar_tabela():
    conn = None
    try:
        conn = sqlite3.connect('alugueis.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        print("Tabela 'usuarios' verificada/criada com sucesso!")
        conn.commit()

    except sqlite3.Error as e:
        print(f"Erro ao criar la tabela de usuários: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    criar_tabela()