from flask import Flask, request, jsonify
import json, os
from datetime import datetime, timedelta

app = Flask(__name__)
DB_FILE = "users.json"
CONFIG_FILE = "config.json"

def init_db():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f: json.dump({"ativo": True}, f)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"AdryanSoftware7392841056": {"status": "active", "ip_fixo": None, "cargo": "Fundador", "expira": "2030-01-01", "nome": "Adryan"}}, f)

@app.route('/auth', methods=['POST'])
def auth():
    init_db()
    data = request.json
    key = data.get("key")
    ip_atual = request.remote_addr
    with open(DB_FILE, "r") as f: db = json.load(f)
    if key not in db: return jsonify({"msg": "KEY INVALIDA"}), 403
    user = db[key]
    if user["status"] == "blocked": return jsonify({"msg": "KEY BLOQUEADA"}), 403
    if user["ip_fixo"] is None:
        user["ip_fixo"] = ip_atual
        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
    elif user["ip_fixo"] != ip_atual:
        return jsonify({"msg": "OUTRO IP TENTANDO USAR"}), 403
    return jsonify({"msg": "Sucesso", "cargo": user["cargo"], "nome": user.get("nome", "Usuario")})

# NOVO: Ver quem está usando (Opção 5)
@app.route('/admin/users', methods=['GET'])
def list_users():
    with open(DB_FILE, "r") as f: return jsonify(json.load(f))

# NOVO: Bloquear/Renovar (Opções 1 e 2)
@app.route('/admin/manage', methods=['POST'])
def manage():
    data = request.json
    if data.get("admin_key") != "AdryanSoftware7392841056": return jsonify({"msg": "ERRO"}), 403
    with open(DB_FILE, "r") as f: db = json.load(f)
    
    target = data.get("target_key")
    if target in db:
        if data["action"] == "block": db[target]["status"] = "blocked"
        if data["action"] == "renew": db[target]["status"] = "active"
        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
    return jsonify({"msg": "OK"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
