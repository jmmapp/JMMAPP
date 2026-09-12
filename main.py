from flask import Flask, jsonify, request, session, redirect
import requests
import secrets
import hashlib
import base64
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "chave-local-desenvolvimento"
)

def gerar_pkce():
    code_verifier = secrets.token_urlsafe(64)

    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")

    return code_verifier, code_challenge

@app.route("/login")
def login():
    code_verifier, code_challenge = gerar_pkce()

    state = secrets.token_urlsafe(32)

    session["code_verifier"] = code_verifier
    session["state"] = state

    client_id = "8942997963391701"
    redirect_uri = "https://jmmapp.vercel.app/callback"

    url = (
        "https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&state={state}"
    )

    return redirect(url)

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
    state = request.args.get("state")

    if not code:
        return jsonify({
            "status": "erro",
            "mensagem": "Nenhum código de autorização foi recebido."
        }), 400

    state_salvo = session.get("state")

    if not state or state != state_salvo:
        return jsonify({
            "status": "erro",
            "mensagem": "State inválido."
        }), 400

    code_verifier = session.get("code_verifier")

    if not code_verifier:
        return jsonify({
            "status": "erro",
            "mensagem": "Code verifier não encontrado na sessão."
        }), 400

    url = "https://api.mercadolibre.com/oauth/token"

    dados = {
        "grant_type": "authorization_code",
        "client_id": "8942997963391701",
        "client_secret": os.environ.get("ML_CLIENT_SECRET"),
        "code": code,
        "redirect_uri": "https://jmmapp.vercel.app/callback",
        "code_verifier": code_verifier
    }

    response = requests.post(url, data=dados)

    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    token_data = response.json()

    session["access_token"] = token_data["access_token"]
    session["user_id"] = token_data["user_id"]

    return jsonify({
        "status": "sucesso",
        "mensagem": "Autorização concluída com sucesso."
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