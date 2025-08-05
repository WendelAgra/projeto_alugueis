# atualizar_banco.py
import sqlite3

def adicionar_coluna_apelido():
    """Adiciona a coluna 'apelido' à tabela 'casas' se ela não existir."""
    conn = None
    try:
        conn = sqlite3.connect('alugueis.db')
        cursor = conn.cursor()
        
        # Verifica se a coluna já existe
        cursor.execute("PRAGMA table_info(casas)")
        colunas = [coluna[1] for coluna in cursor.fetchall()]
        
        if 'apelido' not in colunas:
            cursor.execute('ALTER TABLE casas ADD COLUMN apelido TEXT')
            print("Coluna 'apelido' adicionada à tabela 'casas' com sucesso!")
        else:
            print("Coluna 'apelido' já existe.")
            
        conn.commit()

    except sqlite3.Error as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    adicionar_coluna_apelido()