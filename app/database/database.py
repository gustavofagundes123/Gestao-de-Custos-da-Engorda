import sqlite3

DATABASE = "custos.db"


def conectar():
    conexao = sqlite3.connect(DATABASE)
    return conexao


def criar_tabela():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS custos_alimentacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo_alimentacao TEXT NOT NULL,
            valor REAL NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()