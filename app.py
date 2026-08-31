from flask import Flask, render_template, request, redirect, url_for
from app.database.database import criar_tabela, conectar

app = Flask(__name__)

criar_tabela()


@app.route("/")
def inicio():
    return render_template("cadastro_custo.html")


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    data = request.form["data"]
    tipo = request.form["tipo_alimentacao"]
    valor = request.form["valor"]

    conexao = conectar()

    conexao.execute(
        """
        INSERT INTO custos_alimentacao
        (data, tipo_alimentacao, valor)
        VALUES (?, ?, ?)
        """,
        (data, tipo, valor)
    )

    conexao.commit()
    conexao.close()

    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)