import sqlite3
import pandas as pd

db_file = 'alugueis.db'
conn = sqlite3.connect(db_file)
try:
    # Lê os dados da tabela antiga
    df = pd.read_sql_query("SELECT * FROM alugueis", conn)

    # Renomeia a tabela antiga
    conn.execute('ALTER TABLE alugueis RENAME TO alugueis_old')

    # Cria a nova tabela com a estrutura correta (sem a restrição NOT NULL em mes_referencia)
    conn.execute('''
        CREATE TABLE alugueis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            casa_id INTEGER NOT NULL,
            inquilino_id INTEGER,
            mes_referencia TEXT, 
            pago INTEGER NOT NULL DEFAULT 0,
            data_vencimento TEXT,
            valor_aluguel REAL,
            FOREIGN KEY (casa_id) REFERENCES casas (id),
            FOREIGN KEY (inquilino_id) REFERENCES inquilinos (id)
        )
    ''')

    # Insere os dados antigos na nova tabela
    df.to_sql('alugueis', conn, if_exists='append', index=False)

    # Apaga a tabela antiga
    conn.execute('DROP TABLE alugueis_old')

    print("Tabela 'alugueis' recriada com sucesso para remover a restrição NOT NULL.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
    print("A restaurar a tabela antiga...")
    # Tenta restaurar em caso de erro
    try:
        conn.execute('DROP TABLE alugueis')
        conn.execute('ALTER TABLE alugueis_old RENAME TO alugueis')
    except:
        pass # A restauração pode falhar se o erro ocorreu no início
finally:
    conn.close()