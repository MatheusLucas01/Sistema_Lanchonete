import sqlite3
from .database import executar_query
from .produtos import listar_produtos

def registrar_venda(produto_id, quantidade):
    """Registra uma venda e atualiza o estoque"""
    # Verifica se há estoque suficiente
    conn = sqlite3.connect('lanches.db')
    cursor = conn.cursor()
    cursor.execute("SELECT estoque FROM produtos WHERE id = ?", (produto_id,))
    estoque_atual = cursor.fetchone()[0]
    conn.close()
    
    if estoque_atual < quantidade:
        raise ValueError("Estoque insuficiente")
    
    # Registra a venda e atualiza o estoque
    executar_query(
        "INSERT INTO vendas (produto_id, quantidade) VALUES (?, ?)",
        (produto_id, quantidade)
    )
    executar_query(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id)
    )