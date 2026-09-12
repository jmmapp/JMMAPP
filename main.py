from flask import Flask, jsonify, request
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "mensagem": "JMM Promos API está funcionando"
    })


@app.route("/perfumes")
def perfumes():
    url = "https://api.mercadolibre.com/sites/MLB/search?q=perfume"

    response = requests.get(url)

    return jsonify(response.json())


@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return jsonify({
            "status": "erro",
            "mensagem": "Nenhum código de autorização foi recebido."
        }), 400

    return jsonify({
        "status": "sucesso",
        "mensagem": "Código de autorização recebido.",
        "code": code
    })

@app.route("/notifications", methods=["POST"])
def notifications():
    data = request.json

    print("Notificação recebida:")
    print(data)

    return jsonify({
        "status": "ok"
    }), 200

if __name__ == "__main__":
    app.run()