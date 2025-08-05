# atualizar_tabela_alugueis.py
import sqlite3

conn = sqlite3.connect('alugueis.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE alugueis ADD COLUMN valor_aluguel REAL')
    print("Coluna 'valor_aluguel' adicionada a 'alugueis'.")
except sqlite3.OperationalError:
    print("Coluna 'valor_aluguel' já existe em 'alugueis'.")

conn.commit()
conn.close()