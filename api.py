from flask import Flask, request, jsonify
import json, os

app = Flask(__name__)
DB_FILE = "users.json"
BAN_FILE = "bans.json"

def init_db():
    if not os.path.exists(DB_FILE):
        json.dump({"AdryanSoftware7392841056": {"status": "active", "ip_fixo": None, "cargo": "Fundador", "nome": "Adryan"}}, open(DB_FILE, "w"))
    if not os.path.exists(BAN_FILE):
        json.dump([], open(BAN_FILE, "w"))

@app.route('/auth', methods=['POST'])
def auth():
    init_db()
    ip_atual = request.remote_addr
    with open(BAN_FILE, "r") as f: bans = json.load(f)
    if ip_atual in bans: return jsonify({"msg": "VOCE ESTA BANIDO PERMANENTEMENTE"}), 403
    
    data = request.json
    key = data.get("key")
    with open(DB_FILE, "r") as f: db = json.load(f)
    if key not in db: return jsonify({"msg": "KEY INVALIDA"}), 403
    
    user = db[key]
    if user["ip_fixo"] is None:
        user["ip_fixo"] = ip_atual
        json.dump(db, open(DB_FILE, "w"), indent=4)
    elif user["ip_fixo"] != ip_atual:
        return jsonify({"msg": "OUTRO IP TENTANDO USAR"}), 403
    return jsonify({"msg": "Sucesso", "cargo": user["cargo"]})

@app.route('/admin/ban', methods=['POST'])
def manage_ban():
    data = request.json
    if data.get("admin_key") != "AdryanSoftware7392841056": return jsonify({"msg": "ERRO"}), 403
    with open(BAN_FILE, "r") as f: bans = json.load(f)
    
    ip = data.get("ip")
    if data["action"] == "ban":
        if ip not in bans: bans.append(ip)
    elif data["action"] == "unban":
        if ip in bans: bans.remove(ip)
        
    json.dump(bans, open(BAN_FILE, "w"), indent=4)
    return jsonify({"msg": "OK"})

@app.route('/admin/banlist', methods=['GET'])
def banlist():
    return jsonify(json.load(open(BAN_FILE, "r")))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
