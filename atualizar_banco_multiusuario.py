# atualizar_banco_multiusuario.py
import sqlite3

def adicionar_colunas_usuario():
    db_file = 'alugueis.db'
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Adiciona a coluna 'usuario_id' à tabela 'casas'
        try:
            cursor.execute('ALTER TABLE casas ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)')
            print("Coluna 'usuario_id' adicionada a 'casas'.")
        except sqlite3.OperationalError:
            print("Coluna 'usuario_id' já existe em 'casas'.")

        # Adiciona a coluna 'usuario_id' à tabela 'inquilinos'
        try:
            cursor.execute('ALTER TABLE inquilinos ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)')
            print("Coluna 'usuario_id' adicionada a 'inquilinos'.")
        except sqlite3.OperationalError:
            print("Coluna 'usuario_id' já existe em 'inquilinos'.")

        # **MUITO IMPORTANTE**: Associa todos os dados existentes ao primeiro usuário (ID = 1)
        # Isso garante que seus dados antigos não fiquem "perdidos".
        cursor.execute("UPDATE casas SET usuario_id = 1 WHERE usuario_id IS NULL")
        cursor.execute("UPDATE inquilinos SET usuario_id = 1 WHERE usuario_id IS NULL")
        print("Dados existentes associados ao usuário de ID 1.")
        
        conn.commit()

    except sqlite3.Error as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    adicionar_colunas_usuario()