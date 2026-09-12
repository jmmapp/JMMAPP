from flask import Flask, jsonify
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


if __name__ == "__main__":
    app.run()