import sqlite3

def criar_banco():
    """Cria o banco de dados e tabelas se não existirem"""
    conn = sqlite3.connect('lanches.db')
    cursor = conn.cursor()
    
    # Tabela de produtos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        estoque INTEGER NOT NULL
    )
    ''')
    
    # Tabela de vendas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insere produtos de exemplo, se não houver nenhum
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        produtos_exemplo = [
            ('X-Burger', 15.90, 50),
            ('Refrigerante', 7.50, 100),
            ('Batata Frita', 12.00, 30)
        ]
        cursor.executemany(
            "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
            produtos_exemplo
        )
    
    conn.commit()
    conn.close()

def executar_query(query, params=()):
    conn = None
    try:
        conn = sqlite3.connect('lanches.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro na query: {query}\nParâmetros: {params}\nErro: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

# Adicione estas linhas no final do arquivo para testar
if __name__ == "__main__":
    criar_banco()
    print("Banco criado com sucesso!")
    produtos = executar_query("SELECT * FROM produtos")
    print("Produtos cadastrados:", produtos)
