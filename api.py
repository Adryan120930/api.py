from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json, os

app = Flask(__name__)
DB_FILE = "users.json"
CONFIG_FILE = "config.json"

def init_db():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f: json.dump({"ativo": True}, f)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            # Sua key de fundador com IP liberado inicialmente (None)
            json.dump({"AdryanSoftware7392841056": {"status": "active", "ip_fixo": None, "cargo": "Fundador", "expira": "2030-01-01"}}, f)

@app.route('/auth', methods=['POST'])
def auth():
    init_db()
    with open(CONFIG_FILE, "r") as f: config = json.load(f)
    data = request.json
    key = data.get("key")
    ip_atual = request.remote_addr # Pega o IP real do usuário

    if not config["ativo"] and key != "AdryanSoftware7392841056":
        return jsonify({"msg": "SISTEMA DESABILITADO"}), 403

    with open(DB_FILE, "r") as f: db = json.load(f)
    if key not in db: return jsonify({"msg": "KEY INVALIDA"}), 403
    
    user = db[key]
    
    # TRAVA POR IP (Em vez de HWID)
    if user["ip_fixo"] is None:
        user["ip_fixo"] = ip_atual
        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
    elif user["ip_fixo"] != ip_atual:
        return jsonify({"msg": "BLOQUEADO: ESSA KEY PERTENCE A OUTRO IP"}), 403

    return jsonify({"msg": "Sucesso", "cargo": user["cargo"]})

@app.route('/admin/config', methods=['POST'])
def admin_config():
    data = request.json
    if data.get("key") != "AdryanSoftware7392841056": return jsonify({"msg": "ERRO"}), 403
    with open(CONFIG_FILE, "w") as f: json.dump({"ativo": data["set_ativo"]}, f)
    return jsonify({"msg": "OK"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
