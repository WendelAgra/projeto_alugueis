# criar_tabela_contratos.py
import sqlite3

def criar_tabela():
    conn = None
    try:
        conn = sqlite3.connect('alugueis.db')
        cursor = conn.cursor()
        
        # Cria a nova tabela de contratos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            casa_id INTEGER NOT NULL,
            inquilino_id INTEGER NOT NULL,
            valor_aluguel REAL NOT NULL,
            dia_vencimento INTEGER NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT,
            status TEXT NOT NULL DEFAULT 'ativo',
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (casa_id) REFERENCES casas (id),
            FOREIGN KEY (inquilino_id) REFERENCES inquilinos (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
        ''')
        print("Tabela 'contratos' verificada/criada com sucesso!")
        conn.commit()

    except sqlite3.Error as e:
        print(f"Erro ao criar a tabela de contratos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    criar_tabela()