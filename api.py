from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json, os

app = Flask(__name__)
DB_FILE = "users.json"
LOG_FILE = "logs.json"
BANS_FILE = "bans.json"

# Inicializa banco de dados
def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"AdryanSoftware7392841056": {"status": "active", "hwid": None, "cargo": "Fundador", "expira": "2030-01-01"}}, f)

@app.route('/auth', methods=['POST'])
def auth():
    init_db()
    data = request.json
    key, hwid, ip = data.get("key"), data.get("hwid"), request.remote_addr
    
    # 1. Checa Ban de IP
    if os.path.exists(BANS_FILE):
        with open(BANS_FILE, "r") as f:
            if ip in json.load(f): return jsonify({"msg": "IP BANIDO"}), 403

    # 2. Checa Key
    with open(DB_FILE, "r") as f: db = json.load(f)
    if key not in db: return jsonify({"msg": "KEY INEXISTENTE"}), 403

    user = db[key]
    
    # 3. Checa Expiração
    if datetime.strptime(user["expira"], "%Y-%m-%d") < datetime.now():
        return jsonify({"msg": "ASSINATURA EXPIRADA"}), 403

    # 4. Trava HWID
    if user["hwid"] is None:
        user["hwid"] = hwid
        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
    elif user["hwid"] != hwid:
        return jsonify({"msg": "OUTRO PC TENTANDO USAR"}), 403

    # 5. Salva Log
    log_entry = {"data": datetime.now().strftime("%H:%M:%S"), "ip": ip, "hwid": hwid, "key": key}
    try:
        with open(LOG_FILE, "r") as f: logs = json.load(f)
    except: logs = []
    logs.append(log_entry)
    with open(LOG_FILE, "w") as f: json.dump(logs, f, indent=4)

    return jsonify({"msg": "Sucesso", "cargo": user["cargo"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)