from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "chave-secreta"

DATABASE = "banco.db"


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
            unidade TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


@app.route("/")
def index():
    conexao = conectar_banco()

    insumos = conexao.execute(
        "SELECT * FROM insumos ORDER BY id DESC"
    ).fetchall()

    conexao.close()

    return render_template("index.html", insumos=insumos)


@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        quantidade = request.form.get("quantidade", "").strip()
        unidade = request.form.get("unidade", "").strip()

        if not nome or not quantidade or not unidade:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return render_template("cadastrar.html")

        try:
            quantidade = float(quantidade)

            if quantidade <= 0:
                flash("A quantidade deve ser maior que zero.", "erro")
                return render_template("cadastrar.html")

        except ValueError:
            flash("Digite uma quantidade válida.", "erro")
            return render_template("cadastrar.html")

        conexao = conectar_banco()

        conexao.execute("""
            INSERT INTO insumos (nome, quantidade, unidade)
            VALUES (?, ?, ?)
        """, (nome, quantidade, unidade))

        conexao.commit()
        conexao.close()

        flash("Insumo cadastrado com sucesso!", "sucesso")

        return redirect(url_for("index"))

    return render_template("cadastrar.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexao = conectar_banco()

    insumo = conexao.execute(
        "SELECT * FROM insumos WHERE id = ?",
        (id,)
    ).fetchone()

    if insumo is None:
        conexao.close()
        flash("Insumo não encontrado.", "erro")
        return redirect(url_for("index"))

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        quantidade = request.form.get("quantidade", "").strip()
        unidade = request.form.get("unidade", "").strip()

        if not nome or not quantidade or not unidade:
            conexao.close()
            flash("Preencha todos os campos obrigatórios.", "erro")
            return render_template("editar.html", insumo=insumo)

        try:
            quantidade = float(quantidade)

            if quantidade <= 0:
                conexao.close()
                flash("A quantidade deve ser maior que zero.", "erro")
                return render_template("editar.html", insumo=insumo)

        except ValueError:
            conexao.close()
            flash("Digite uma quantidade válida.", "erro")
            return render_template("editar.html", insumo=insumo)

        conexao.execute("""
            UPDATE insumos
            SET nome = ?, quantidade = ?, unidade = ?
            WHERE id = ?
        """, (nome, quantidade, unidade, id))

        conexao.commit()
        conexao.close()

        flash("Insumo atualizado com sucesso!", "sucesso")

        return redirect(url_for("index"))

    conexao.close()

    return render_template("editar.html", insumo=insumo)


@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM insumos WHERE id = ?",
        (id,)
    )

    conexao.commit()
    conexao.close()

    flash("Insumo excluído com sucesso!", "sucesso")

    return redirect(url_for("index"))


if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)