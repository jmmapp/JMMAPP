from flask import Flask, jsonify, request, session, redirect
import requests
import secrets
import hashlib
import base64
import os
import re

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
    access_token = session.get("access_token")

    if not access_token:
        return jsonify({
            "status": "erro",
            "mensagem": "Nenhum access token encontrado. Faça login novamente."
        }), 401

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    url = "https://api.mercadolibre.com/sites/MLB/search?q=perfume"

    response = requests.get(url, headers=headers)

    return jsonify(response.json()), response.status_code


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

@app.route("/teste-api")
def teste_api():
    access_token = session.get("access_token")

    if not access_token:
        return jsonify({
            "status": "erro",
            "mensagem": "Nenhum access token encontrado. Faça login novamente."
        }), 401

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        "https://api.mercadolibre.com/users/me",
        headers=headers
    )

    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    usuario = response.json()

    return jsonify({
        "status": "sucesso",
        "id": usuario.get("id"),
        "nickname": usuario.get("nickname"),
        "site_id": usuario.get("site_id")
    })

@app.route("/produto-teste")
def produto_teste():
    access_token = session.get("access_token")

    if not access_token:
        return jsonify({
            "status": "erro",
            "mensagem": "Nenhum access token encontrado. Faça login novamente."
        }), 401

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    item_id = "MLB2036110657"

    url = f"https://api.mercadolibre.com/items/{item_id}"

    response = requests.get(url, headers=headers)

    return jsonify(response.json()), response.status_code

@app.route("/pagina-teste")
def pagina_teste():
    url = (
        "https://www.mercadolivre.com.br/"
        "perfume-jean-paul-gaultier-le-male-eau-de-parfum-intense-75-ml-masculino/"
        "p/MLB17512827"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/152.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15,
        allow_redirects=True
    )

    return jsonify({
        "status_http": response.status_code,
        "acesso": response.ok,
        "tamanho_html": len(response.text),
        "url_final": response.url
    })

@app.route("/recomendacao-teste")
def recomendacao_teste():
    url = (
        "https://www.mercadolivre.com.br/social/"
        "jz20260905175617996/lists/"
        "f524c20d-1e3b-4eb7-881a-61fef471ef9a"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/152.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    html = response.text

    links_encontrados = re.findall(
    r'href=["\']([^"\']*MLB\d+[^"\']*)["\']',
    html
)

    links_unicos = list(dict.fromkeys(links_encontrados))

    return jsonify({
    "status_http": response.status_code,
    "quantidade_links": len(links_unicos),
    "links": links_unicos[:30]
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