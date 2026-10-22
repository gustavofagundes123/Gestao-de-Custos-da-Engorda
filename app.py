
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import sys

# Permite importar arquivos da pasta src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from custo_engorda import calcular_custo_por_kg

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-secreta")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "banco.db")

UNIDADES_PERMITIDAS = ("kg", "g", "L", "mL", "un", "Saco")
PESOS_SACO_PERMITIDOS = (15, 20, 25, 30, 35, 40)


def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS insumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade REAL NOT NULL,
            unidade TEXT NOT NULL,
            preco_total REAL NOT NULL DEFAULT 0,
            peso_por_saco REAL
        )
    """)

    # Atualiza bancos antigos sem apagar os registros existentes
    colunas = {
        coluna["name"]
        for coluna in conexao.execute(
            "PRAGMA table_info(insumos)"
        ).fetchall()
    }

    if "preco_total" not in colunas:
        conexao.execute("""
            ALTER TABLE insumos
            ADD COLUMN preco_total REAL NOT NULL DEFAULT 0
        """)

    if "peso_por_saco" not in colunas:
        conexao.execute("""
            ALTER TABLE insumos
            ADD COLUMN peso_por_saco REAL
        """)

    conexao.commit()
    conexao.close()


def converter_numero(valor):
    """Aceita números com ponto ou vírgula decimal."""
    return float(valor.strip().replace(",", "."))


def buscar_insumos():
    conexao = conectar_banco()
    insumos = conexao.execute(
        "SELECT * FROM insumos ORDER BY id DESC"
    ).fetchall()
    conexao.close()
    return insumos


def buscar_insumo(id):
    conexao = conectar_banco()
    insumo = conexao.execute(
        "SELECT * FROM insumos WHERE id = ?",
        (id,)
    ).fetchone()
    conexao.close()
    return insumo


def validar_insumo(formulario):
    nome = formulario.get("nome", "").strip()
    quantidade_texto = formulario.get("quantidade", "").strip()
    unidade = formulario.get("unidade", "").strip()
    preco_texto = formulario.get("preco_total", "").strip()
    peso_saco_texto = formulario.get("peso_por_saco", "").strip()

    if not nome or not quantidade_texto or not unidade or not preco_texto:
        raise ValueError("Preencha todos os campos obrigatórios.")

    if unidade not in UNIDADES_PERMITIDAS:
        raise ValueError("Selecione uma unidade de medida válida.")

    quantidade = converter_numero(quantidade_texto)
    preco_total = converter_numero(preco_texto)

    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    if preco_total <= 0:
        raise ValueError("O preço total deve ser maior que zero.")

    peso_por_saco = None

    if unidade == "Saco":
        if not peso_saco_texto:
            raise ValueError("Informe o peso de cada saco.")

        peso_por_saco = converter_numero(peso_saco_texto)

        if peso_por_saco not in PESOS_SACO_PERMITIDOS:
            raise ValueError(
                "Selecione um peso de saco permitido: "
                "15, 20, 25, 30, 35 ou 40 kg."
            )

    return nome, quantidade, unidade, preco_total, peso_por_saco


@app.route("/")
def index():
    insumos = buscar_insumos()

    custo_total = sum(insumo["preco_total"] for insumo in insumos)

    peso_total_sacos = sum(
        insumo["quantidade"] * insumo["peso_por_saco"]
        for insumo in insumos
        if insumo["unidade"] == "Saco"
        and insumo["peso_por_saco"] is not None
    )

    return render_template(
        "index.html",
        insumos=insumos,
        custo_total=custo_total,
        peso_total_sacos=peso_total_sacos
    )


@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        try:
            dados = validar_insumo(request.form)
        except ValueError as erro:
            flash(str(erro), "erro")
            return render_template("cadastrar.html")

        conexao = conectar_banco()
        conexao.execute("""
            INSERT INTO insumos
                (nome, quantidade, unidade, preco_total, peso_por_saco)
            VALUES (?, ?, ?, ?, ?)
        """, dados)
        conexao.commit()
        conexao.close()

        flash("Insumo cadastrado com sucesso!", "sucesso")
        return redirect(url_for("index"))

    return render_template("cadastrar.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    insumo = buscar_insumo(id)

    if insumo is None:
        flash("Insumo não encontrado.", "erro")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            dados = validar_insumo(request.form)
        except ValueError as erro:
            flash(str(erro), "erro")
            return render_template("editar.html", insumo=insumo)

        conexao = conectar_banco()
        conexao.execute("""
            UPDATE insumos
            SET nome = ?,
                quantidade = ?,
                unidade = ?,
                preco_total = ?,
                peso_por_saco = ?
            WHERE id = ?
        """, (*dados, id))
        conexao.commit()
        conexao.close()

        flash("Insumo atualizado com sucesso!", "sucesso")
        return redirect(url_for("index"))

    return render_template("editar.html", insumo=insumo)


@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conexao = conectar_banco()
    conexao.execute("DELETE FROM insumos WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()

    flash("Insumo excluído com sucesso!", "sucesso")
    return redirect(url_for("index"))


@app.route("/calcular", methods=["POST"])
def calcular():
    try:
        peso_inicial = converter_numero(
            request.form.get("peso_inicial", "")
        )
        peso_final = converter_numero(
            request.form.get("peso_final", "")
        )

        if peso_inicial <= 0 or peso_final <= 0:
            raise ValueError("Os pesos devem ser maiores que zero.")

        if peso_final <= peso_inicial:
            raise ValueError(
                "O peso final deve ser maior que o peso inicial."
            )

        insumos = buscar_insumos()

        if not insumos:
            raise ValueError(
                "Cadastre os insumos e seus preços antes de calcular."
            )

        if any(insumo["preco_total"] <= 0 for insumo in insumos):
            raise ValueError(
                "Existe insumo sem preço válido. Edite os insumos "
                "cadastrados e informe o preço total de cada um."
            )

        custo_total = sum(
            insumo["preco_total"] for insumo in insumos
        )

        custo_por_kg = calcular_custo_por_kg(
            custo_total,
            peso_inicial,
            peso_final
        )

        return render_template(
            "index.html",
            insumos=insumos,
            custo_total=custo_total,
            peso_total_sacos=sum(
                insumo["quantidade"] * insumo["peso_por_saco"]
                for insumo in insumos
                if insumo["unidade"] == "Saco"
                and insumo["peso_por_saco"] is not None
            ),
            custo_por_kg=custo_por_kg,
            peso_inicial=peso_inicial,
            peso_final=peso_final
        )

    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("index"))


# Cria ou atualiza a estrutura do banco
criar_tabela()


if __name__ == "__main__":
    app.run(debug=True)
