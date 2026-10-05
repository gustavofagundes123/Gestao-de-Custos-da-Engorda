from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import sys
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# IMPORTAÇÃO
# =========================================================

sys.path.append(
    os.path.join(os.path.dirname(__file__), "src")
)

from custo_engorda import calcular_custo_por_kg


# =========================================================
# CONFIGURAÇÃO
# =========================================================

app = Flask(__name__)

app.secret_key = "chave-secreta"


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE = os.path.join(
    BASE_DIR,
    "banco.db"
)


# =========================================================
# BANCO DE DADOS
# =========================================================

def conectar_banco():

    conexao = sqlite3.connect(DATABASE)

    conexao.row_factory = sqlite3.Row

    return conexao


# =========================================================
# PROTEÇÃO DE LOGIN
# =========================================================

def login_required(func):

    @wraps(func)
    def verificar_login(*args, **kwargs):

        if "usuario_id" not in session:

            flash(
                "Faça login para acessar o sistema.",
                "erro"
            )

            return redirect(
                url_for("login")
            )

        return func(*args, **kwargs)

    return verificar_login


# =========================================================
# CRIAÇÃO E ATUALIZAÇÃO DO BANCO
# =========================================================

def criar_tabela():

    conexao = conectar_banco()


    # -----------------------------------------------------
    # TABELA DE USUÁRIOS
    # -----------------------------------------------------

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL,

            email TEXT NOT NULL UNIQUE,

            senha TEXT NOT NULL

        )
    """)


    # -----------------------------------------------------
    # USUÁRIO ADMINISTRADOR
    # -----------------------------------------------------

    usuario = conexao.execute("""
        SELECT id
        FROM usuarios
        WHERE email = ?
    """, (
        "admin@engorda.com",
    )).fetchone()


    if usuario is None:

        senha_hash = generate_password_hash(
            "123456"
        )

        conexao.execute("""
            INSERT INTO usuarios
            (
                nome,
                email,
                senha
            )
            VALUES (?, ?, ?)
        """, (
            "Administrador",
            "admin@engorda.com",
            senha_hash
        ))


    # -----------------------------------------------------
    # TABELA DE INSUMOS
    # -----------------------------------------------------

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS insumos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL,

            quantidade REAL NOT NULL,

            unidade TEXT NOT NULL,

            custo_unitario REAL NOT NULL DEFAULT 0

        )
    """)


    # -----------------------------------------------------
    # VERIFICA COLUNAS DA TABELA
    # -----------------------------------------------------

    colunas = conexao.execute(
        "PRAGMA table_info(insumos)"
    ).fetchall()


    nomes_colunas = [
        coluna["name"]
        for coluna in colunas
    ]


    # Adiciona custo_unitario em bancos antigos
    if "custo_unitario" not in nomes_colunas:

        conexao.execute("""
            ALTER TABLE insumos

            ADD COLUMN custo_unitario
            REAL NOT NULL DEFAULT 0
        """)


    # -----------------------------------------------------
    # ADICIONA USUARIO_ID
    # -----------------------------------------------------

    if "usuario_id" not in nomes_colunas:

        conexao.execute("""
            ALTER TABLE insumos

            ADD COLUMN usuario_id
            INTEGER
        """)


    conexao.commit()


    # -----------------------------------------------------
    # VINCULA DADOS ANTIGOS AO ADMINISTRADOR
    # -----------------------------------------------------

    admin = conexao.execute("""
        SELECT id
        FROM usuarios
        WHERE email = ?
    """, (
        "admin@engorda.com",
    )).fetchone()


    if admin:

        conexao.execute("""
            UPDATE insumos

            SET usuario_id = ?

            WHERE usuario_id IS NULL
        """, (
            admin["id"],
        ))


    conexao.commit()

    conexao.close()


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if "usuario_id" in session:

        return redirect(
            url_for("index")
        )


    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()


        senha = request.form.get(
            "senha",
            ""
        )


        if not email or not senha:

            flash(
                "Preencha o e-mail e a senha.",
                "erro"
            )

            return render_template(
                "login.html"
            )


        conexao = conectar_banco()


        usuario = conexao.execute("""
            SELECT *
            FROM usuarios

            WHERE email = ?
        """, (
            email,
        )).fetchone()


        conexao.close()


        if (
            usuario
            and check_password_hash(
                usuario["senha"],
                senha
            )
        ):

            session["usuario_id"] = usuario["id"]

            session["usuario_nome"] = usuario["nome"]

            session["usuario_email"] = usuario["email"]


            flash(
                "Login realizado com sucesso!",
                "sucesso"
            )


            return redirect(
                url_for("index")
            )


        flash(
            "E-mail ou senha incorretos.",
            "erro"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# CADASTRO DE USUÁRIO
# =========================================================

@app.route(
    "/cadastro",
    methods=["GET", "POST"]
)
def cadastro():

    if "usuario_id" in session:

        return redirect(
            url_for("index")
        )


    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()


        email = request.form.get(
            "email",
            ""
        ).strip().lower()


        senha = request.form.get(
            "senha",
            ""
        )


        confirmar_senha = request.form.get(
            "confirmar_senha",
            ""
        )


        # -------------------------------------------------
        # CAMPOS OBRIGATÓRIOS
        # -------------------------------------------------

        if (
            not nome
            or not email
            or not senha
            or not confirmar_senha
        ):

            flash(
                "Preencha todos os campos.",
                "erro"
            )

            return render_template(
                "cadastro_usuario.html"
            )


        # -------------------------------------------------
        # SENHA
        # -------------------------------------------------

        if len(senha) < 6:

            flash(
                "A senha deve ter pelo menos 6 caracteres.",
                "erro"
            )

            return render_template(
                "cadastro_usuario.html"
            )


        if senha != confirmar_senha:

            flash(
                "As senhas não são iguais.",
                "erro"
            )

            return render_template(
                "cadastro_usuario.html"
            )


        # -------------------------------------------------
        # VERIFICA E-MAIL
        # -------------------------------------------------

        conexao = conectar_banco()


        usuario_existente = conexao.execute("""
            SELECT id
            FROM usuarios

            WHERE email = ?
        """, (
            email,
        )).fetchone()


        if usuario_existente:

            conexao.close()

            flash(
                "Este e-mail já está cadastrado.",
                "erro"
            )

            return render_template(
                "cadastro_usuario.html"
            )


        # -------------------------------------------------
        # CRIA USUÁRIO
        # -------------------------------------------------

        senha_hash = generate_password_hash(
            senha
        )


        conexao.execute("""
            INSERT INTO usuarios
            (
                nome,
                email,
                senha
            )
            VALUES (?, ?, ?)
        """, (
            nome,
            email,
            senha_hash
        ))


        conexao.commit()

        conexao.close()


        flash(
            "Cadastro realizado com sucesso! Agora faça login.",
            "sucesso"
        )


        return redirect(
            url_for("login")
        )


    return render_template(
        "cadastro_usuario.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()


    flash(
        "Você saiu do sistema.",
        "sucesso"
    )


    return redirect(
        url_for("login")
    )


# =========================================================
# BUSCAR INSUMOS DO USUÁRIO LOGADO
# =========================================================

def buscar_insumos():

    conexao = conectar_banco()


    insumos = conexao.execute("""
        SELECT
            id,
            nome,
            quantidade,
            unidade,
            custo_unitario,

            (
                quantidade * custo_unitario
            ) AS custo_total

        FROM insumos

        WHERE usuario_id = ?

        ORDER BY id DESC
    """, (
        session["usuario_id"],
    )).fetchall()


    conexao.close()


    return insumos


# =========================================================
# CALCULAR CUSTO TOTAL DO USUÁRIO
# =========================================================

def calcular_custo_total():

    conexao = conectar_banco()


    resultado = conexao.execute("""
        SELECT
            COALESCE(
                SUM(
                    quantidade * custo_unitario
                ),
                0
            ) AS total

        FROM insumos

        WHERE usuario_id = ?
    """, (
        session["usuario_id"],
    )).fetchone()


    conexao.close()


    return float(
        resultado["total"]
    )


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
@login_required
def index():

    insumos = buscar_insumos()

    custo_total = calcular_custo_total()


    return render_template(
        "index.html",

        insumos=insumos,

        custo_total=custo_total
    )


# =========================================================
# CADASTRAR INSUMO
# =========================================================

@app.route(
    "/cadastrar",
    methods=["GET", "POST"]
)
@login_required
def cadastrar():

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()


        quantidade = request.form.get(
            "quantidade",
            ""
        ).strip()


        unidade = request.form.get(
            "unidade",
            ""
        ).strip()


        custo_unitario = request.form.get(
            "custo_unitario",
            ""
        ).strip()


        if (
            not nome
            or not quantidade
            or not unidade
            or not custo_unitario
        ):

            flash(
                "Preencha todos os campos obrigatórios.",
                "erro"
            )

            return render_template(
                "cadastrar.html"
            )


        try:

            quantidade = float(
                quantidade
            )

            custo_unitario = float(
                custo_unitario
            )


            if quantidade <= 0:

                flash(
                    "A quantidade deve ser maior que zero.",
                    "erro"
                )

                return render_template(
                    "cadastrar.html"
                )


            if custo_unitario < 0:

                flash(
                    "O custo não pode ser negativo.",
                    "erro"
                )

                return render_template(
                    "cadastrar.html"
                )


        except ValueError:

            flash(
                "Digite valores numéricos válidos.",
                "erro"
            )

            return render_template(
                "cadastrar.html"
            )


        conexao = conectar_banco()


        conexao.execute("""
            INSERT INTO insumos
            (
                nome,
                quantidade,
                unidade,
                custo_unitario,
                usuario_id
            )

            VALUES (?, ?, ?, ?, ?)
        """, (
            nome,
            quantidade,
            unidade,
            custo_unitario,
            session["usuario_id"]
        ))


        conexao.commit()

        conexao.close()


        flash(
            "Insumo cadastrado com sucesso!",
            "sucesso"
        )


        return redirect(
            url_for("index")
        )


    return render_template(
        "cadastrar.html"
    )


# =========================================================
# EDITAR INSUMO
# =========================================================

@app.route(
    "/editar/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def editar(id):

    conexao = conectar_banco()


    # IMPORTANTE:
    # procura pelo ID E pelo usuário logado

    insumo = conexao.execute("""
        SELECT *

        FROM insumos

        WHERE id = ?

        AND usuario_id = ?
    """, (
        id,
        session["usuario_id"]
    )).fetchone()


    if insumo is None:

        conexao.close()


        flash(
            "Insumo não encontrado.",
            "erro"
        )


        return redirect(
            url_for("index")
        )


    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()


        quantidade = request.form.get(
            "quantidade",
            ""
        ).strip()


        unidade = request.form.get(
            "unidade",
            ""
        ).strip()


        custo_unitario = request.form.get(
            "custo_unitario",
            ""
        ).strip()


        if (
            not nome
            or not quantidade
            or not unidade
            or not custo_unitario
        ):

            conexao.close()


            flash(
                "Preencha todos os campos obrigatórios.",
                "erro"
            )


            return render_template(
                "editar.html",
                insumo=insumo
            )


        try:

            quantidade = float(
                quantidade
            )

            custo_unitario = float(
                custo_unitario
            )


            if quantidade <= 0:

                conexao.close()


                flash(
                    "A quantidade deve ser maior que zero.",
                    "erro"
                )


                return render_template(
                    "editar.html",
                    insumo=insumo
                )


            if custo_unitario < 0:

                conexao.close()


                flash(
                    "O custo não pode ser negativo.",
                    "erro"
                )


                return render_template(
                    "editar.html",
                    insumo=insumo
                )


        except ValueError:

            conexao.close()


            flash(
                "Digite valores numéricos válidos.",
                "erro"
            )


            return render_template(
                "editar.html",
                insumo=insumo
            )


        conexao.execute("""
            UPDATE insumos

            SET
                nome = ?,
                quantidade = ?,
                unidade = ?,
                custo_unitario = ?

            WHERE id = ?

            AND usuario_id = ?
        """, (
            nome,
            quantidade,
            unidade,
            custo_unitario,
            id,
            session["usuario_id"]
        ))


        conexao.commit()

        conexao.close()


        flash(
            "Insumo atualizado com sucesso!",
            "sucesso"
        )


        return redirect(
            url_for("index")
        )


    conexao.close()


    return render_template(
        "editar.html",
        insumo=insumo
    )


# =========================================================
# EXCLUIR INSUMO
# =========================================================

@app.route(
    "/excluir/<int:id>",
    methods=["POST"]
)
@login_required
def excluir(id):

    conexao = conectar_banco()


    # Só pode excluir insumo do próprio usuário

    conexao.execute("""
        DELETE FROM insumos

        WHERE id = ?

        AND usuario_id = ?
    """, (
        id,
        session["usuario_id"]
    ))


    conexao.commit()

    conexao.close()


    flash(
        "Insumo excluído com sucesso!",
        "sucesso"
    )


    return redirect(
        url_for("index")
    )


# =========================================================
# CALCULAR CUSTO POR KG
# =========================================================

@app.route(
    "/calcular",
    methods=["POST"]
)
@login_required
def calcular():

    peso_inicial = request.form.get(
        "peso_inicial",
        ""
    ).strip()


    peso_final = request.form.get(
        "peso_final",
        ""
    ).strip()


    try:

        peso_inicial = float(
            peso_inicial
        )

        peso_final = float(
            peso_final
        )


        if (
            peso_inicial <= 0
            or peso_final <= 0
        ):

            flash(
                "Os pesos devem ser maiores que zero.",
                "erro"
            )

            return redirect(
                url_for("index")
            )


        ganho_peso = (
            peso_final
            - peso_inicial
        )


        if ganho_peso <= 0:

            flash(
                "O ganho de peso deve ser maior que zero.",
                "erro"
            )

            return redirect(
                url_for("index")
            )


        # Pega somente os custos
        # do usuário logado

        custo_total = calcular_custo_total()


        if custo_total <= 0:

            flash(
                "Cadastre pelo menos um insumo com custo maior que zero.",
                "erro"
            )

            return redirect(
                url_for("index")
            )


        custo_por_kg = calcular_custo_por_kg(
            custo_total,
            peso_inicial,
            peso_final
        )


        return render_template(
            "index.html",

            insumos=buscar_insumos(),

            custo_total=custo_total,

            peso_inicial=peso_inicial,

            peso_final=peso_final,

            ganho_peso=ganho_peso,

            custo_por_kg=custo_por_kg
        )


    except ValueError:

        flash(
            "Digite valores numéricos válidos.",
            "erro"
        )

        return redirect(
            url_for("index")
        )


# =========================================================
# INICIALIZAÇÃO
# =========================================================

criar_tabela()


if __name__ == "__main__":

    app.run(
        debug=True
    )