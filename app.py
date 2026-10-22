
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
import sqlite3
import os
import sys
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Importa o cálculo de custo
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
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS insumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade REAL NOT NULL,
            unidade TEXT NOT NULL,
            preco_total REAL NOT NULL DEFAULT 0,
            peso_por_saco REAL,
            usuario_id INTEGER
        )
    """)

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

    if "usuario_id" not in colunas:
        conexao.execute("""
            ALTER TABLE insumos
            ADD COLUMN usuario_id INTEGER
        """)

    conexao.commit()
    conexao.close()


def login_required(func):
    @wraps(func)
    def verificar_login(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar o sistema.", "erro")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return verificar_login


def converter_numero(valor):
    return float(valor.strip().replace(",", "."))


def buscar_insumos():
    conexao = conectar_banco()
    insumos = conexao.execute("""
        SELECT *
        FROM insumos
        WHERE usuario_id = ?
        ORDER BY id DESC
    """, (session["usuario_id"],)).fetchall()
    conexao.close()
    return insumos


def buscar_insumo(id):
    conexao = conectar_banco()
    insumo = conexao.execute("""
        SELECT *
        FROM insumos
        WHERE id = ? AND usuario_id = ?
    """, (id, session["usuario_id"])).fetchone()
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

    try:
        quantidade = converter_numero(quantidade_texto)
        preco_total = converter_numero(preco_texto)
    except ValueError:
        raise ValueError("Informe valores numéricos válidos.")

    if quantidade <= 0 or preco_total <= 0:
        raise ValueError("Quantidade e preço devem ser maiores que zero.")

    peso_por_saco = None

    if unidade == "Saco":
        if not peso_saco_texto:
            raise ValueError("Informe o peso de cada saco.")

        try:
            peso_por_saco = converter_numero(peso_saco_texto)
        except ValueError:
            raise ValueError("Informe um peso de saco válido.")

        if peso_por_saco not in PESOS_SACO_PERMITIDOS:
            raise ValueError(
                "O peso do saco deve ser 15, 20, 25, 30, 35 ou 40 kg."
            )

    return nome, quantidade, unidade, preco_total, peso_por_saco


@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not email or not senha:
            flash("Preencha o e-mail e a senha.", "erro")
            return render_template("login.html")

        conexao = conectar_banco()
        usuario = conexao.execute("""
            SELECT *
            FROM usuarios
            WHERE email = ?
        """, (email,)).fetchone()
        conexao.close()

        if usuario and check_password_hash(usuario["senha"], senha):
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_email"] = usuario["email"]
            flash("Login realizado com sucesso!", "sucesso")
            return redirect(url_for("index"))

        flash("E-mail ou senha incorretos.", "erro")

    return render_template("login.html")


@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if "usuario_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        if not nome or not email or not senha or not confirmar_senha:
            flash("Preencha todos os campos.", "erro")
            return render_template("cadastro_usuario.html")

        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "erro")
            return render_template("cadastro_usuario.html")

        if senha != confirmar_senha:
            flash("As senhas não são iguais.", "erro")
            return render_template("cadastro_usuario.html")

        conexao = conectar_banco()

        existente = conexao.execute("""
            SELECT id FROM usuarios WHERE email = ?
        """, (email,)).fetchone()

        if existente:
            conexao.close()
            flash("Este e-mail já está cadastrado.", "erro")
            return render_template("cadastro_usuario.html")

        senha_hash = generate_password_hash(senha)

        try:
            conexao.execute("""
                INSERT INTO usuarios (nome, email, senha)
                VALUES (?, ?, ?)
            """, (nome, email, senha_hash))
            conexao.commit()
        except sqlite3.IntegrityError:
            conexao.close()
            flash("Não foi possível cadastrar esse usuário.", "erro")
            return render_template("cadastro_usuario.html")

        conexao.close()
        flash("Cadastro realizado com sucesso! Agora faça login.", "sucesso")
        return redirect(url_for("login"))

    return render_template("cadastro_usuario.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "sucesso")
    return redirect(url_for("login"))


@app.route("/")
@login_required
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
@login_required
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
                (nome, quantidade, unidade, preco_total,
                 peso_por_saco, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (*dados, session["usuario_id"]))
        conexao.commit()
        conexao.close()

        flash("Insumo cadastrado com sucesso!", "sucesso")
        return redirect(url_for("index"))

    return render_template("cadastrar.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
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
            SET nome = ?, quantidade = ?, unidade = ?,
                preco_total = ?, peso_por_saco = ?
            WHERE id = ? AND usuario_id = ?
        """, (*dados, id, session["usuario_id"]))
        conexao.commit()
        conexao.close()

        flash("Insumo atualizado com sucesso!", "sucesso")
        return redirect(url_for("index"))

    return render_template("editar.html", insumo=insumo)


@app.route("/excluir/<int:id>", methods=["POST"])
@login_required
def excluir(id):
    conexao = conectar_banco()
    conexao.execute("""
        DELETE FROM insumos
        WHERE id = ? AND usuario_id = ?
    """, (id, session["usuario_id"]))
    conexao.commit()
    conexao.close()

    flash("Insumo excluído com sucesso!", "sucesso")
    return redirect(url_for("index"))


@app.route("/calcular", methods=["POST"])
@login_required
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
            raise ValueError("O peso final deve ser maior que o peso inicial.")

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

        custo_total = sum(insumo["preco_total"] for insumo in insumos)

        custo_por_kg = calcular_custo_por_kg(
            custo_total, peso_inicial, peso_final
        )

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
            peso_total_sacos=peso_total_sacos,
            custo_por_kg=custo_por_kg,
            peso_inicial=peso_inicial,
            peso_final=peso_final
        )

    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("index"))


# Cria tabelas ou acrescenta colunas ausentes sem apagar os dados
criar_tabela()


if __name__ == "__main__":
    app.run(debug=True)
