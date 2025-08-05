# atualizar_banco_vencimento.py
import sqlite3

def migrar_para_data_vencimento():
    conn = None
    try:
        conn = sqlite3.connect('alugueis.db')
        cursor = conn.cursor()
        
        # 1. Adiciona a nova coluna, se ela não existir
        try:
            cursor.execute('ALTER TABLE alugueis ADD COLUMN data_vencimento TEXT')
            print("Coluna 'data_vencimento' adicionada com sucesso!")
        except sqlite3.OperationalError:
            print("Coluna 'data_vencimento' já existe.")

        # 2. Copia os dados da coluna antiga para a nova, formatando como data
        cursor.execute("SELECT id, mes_referencia FROM alugueis WHERE data_vencimento IS NULL")
        alugueis_antigos = cursor.fetchall()
        
        for aluguel in alugueis_antigos:
            id_aluguel, mes_ref = aluguel
            if mes_ref:
                # Assume o dia 10 como padrão para os dados antigos
                data_venc = f"{mes_ref}-10"
                cursor.execute("UPDATE alugueis SET data_vencimento = ? WHERE id = ?", (data_venc, id_aluguel))
        
        conn.commit()
        print(f"{len(alugueis_antigos)} registos antigos foram migrados para o novo formato de data.")

    except sqlite3.Error as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrar_para_data_vencimento()