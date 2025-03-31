import sqlite3
from .database import executar_query

def adicionar_produto(nome, preco, estoque):
    executar_query(
        "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
        (nome, preco, estoque)
    )

def listar_produtos():
    conn = sqlite3.connect('lanches.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, preco, estoque FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos