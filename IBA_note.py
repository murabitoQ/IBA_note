from flask import Flask, render_template, jsonify, request, Response, send_from_directory
from db import IC_DB, RC_DB, ChatLogDB
from scraper import Cast_Scraper
import os
import webbrowser
from threading import Timer

app = Flask(__name__)

# DB 初始化
ic_db = IC_DB("db/IC_data.db")
rc_db = RC_DB("db/RC_data.db")
chat_db = ChatLogDB("db/chat_log.db")

# -----------------------------
# 前端首頁
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# IC / RC 最新圖片 API
# -----------------------------
def get_latest_images(base_path):
    """回傳每個資料夾最新一張圖片的 list"""
    result = []
    if not os.path.exists(base_path):
        return result

    for folder in sorted(os.listdir(base_path)):
        folder_path = os.path.join(base_path, folder)
        if not os.path.isdir(folder_path):
            continue

        images = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
        ]
        if not images:
            continue

        images.sort(
            key=lambda x: os.path.getmtime(os.path.join(folder_path, x)),
            reverse=True
        )
        latest_img = os.path.join(base_path, folder, images[0])
        result.append({"folder": folder, "image": "/" + latest_img.replace("\\", "/")})

    return result


@app.route('/IC_images/<path:filename>')
def ic_images(filename):
    return send_from_directory('IC_images', filename)


@app.route('/RC_images/<path:filename>')
def rc_images(filename):
    return send_from_directory('RC_images', filename)


@app.route("/api/ic_latest")
def api_ic_latest():
    return jsonify(get_latest_images("IC_images"))


@app.route("/api/rc_latest")
def api_rc_latest():
    return jsonify(get_latest_images("RC_images"))


# -----------------------------
# Note 區塊資料 API
# -----------------------------
@app.route("/api/note/<type>", methods=["POST"])
def api_note(type):
    data = request.get_json()
    folder_name = data.get("image_src")

    if type == "IC":
        db_data = ic_db.get_data_by_image(folder_name)
    elif type == "RC":
        db_data = rc_db.get_data_by_image(folder_name)
    else:
        db_data = {}

    chat_log = chat_db.get_chat_by_image(folder_name)

    return jsonify({
        "data_content": db_data or {},
        "chat_log": chat_log
    })


# -----------------------------
# ⭐ ChatLog API (整合 routes/chat.py)
# -----------------------------

# 取得留言
@app.route("/chat/<image_src>", methods=["GET"])
def chat_get(image_src):
    logs = chat_db.get_chat_by_image(image_src)
    return jsonify(logs)

from flask import Flask, request, jsonify

# 假設 chat_db 已初始化
# chat_db = ChatLogDB("db/chat_log.db")

# -----------------------------
# 新增留言
# -----------------------------
@app.route("/chat/add", methods=["POST"])
def chat_add():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "msg": "No JSON received"}), 400
    if "image_src" not in data or "text" not in data:
        return jsonify({"status": "error", "msg": "Missing required fields"}), 400

    image_src = data["image_src"]
    text = data["text"].strip()
    if not text:
        return jsonify({"status": "error", "msg": "Empty message"}), 400

    try:
        chat_db.add_entry(image_src, text)
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

    return jsonify({"status": "ok"})

# -----------------------------
# 更新留言
# -----------------------------
@app.route("/chat/update", methods=["POST"])
def chat_update():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "msg": "No JSON received"}), 400
    required = ["image_src", "original_timestamp", "new_content"]
    if any(k not in data for k in required):
        return jsonify({"status": "error", "msg": "Missing required fields"}), 400

    image_src = data["image_src"]
    original_timestamp = data["original_timestamp"]
    new_content = data["new_content"].strip()
    if not new_content:
        return jsonify({"status": "error", "msg": "Empty message"}), 400

    try:
        chat_db.update_entry(image_src, original_timestamp, new_content)
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

    return jsonify({"status": "ok"})

# -----------------------------
# 刪除留言
# -----------------------------
@app.route("/chat/delete", methods=["POST"])
def chat_delete():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "msg": "No JSON received"}), 400
    if "image_src" not in data or "timestamp" not in data:
        return jsonify({"status": "error", "msg": "Missing required fields"}), 400

    try:
        chat_db.delete_entry(data["image_src"], data["timestamp"])
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

    return jsonify({"status": "ok"})

# -----------------------------
# SSE 更新 DB
# -----------------------------
def generate_update(url):
    scraper = Cast_Scraper()
    for msg in scraper.scrape_all(url):
        yield f"data: {msg}\n\n"
    yield "data: ✅ 完成更新\n\n"

@app.route("/api/update_db")
def api_update_db():
    url = request.args.get("url", "https://imaginary-base.jp/cast/")
    return Response(generate_update(url), mimetype="text/event-stream")

# -----------------------------
# 啟動 Flask
# -----------------------------
if __name__ == "__main__":
    port = 5000
    url = f"http://127.0.0.1:{port}/"

    # 只有主程序才執行開瀏覽器
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(0.1, lambda: webbrowser.open(url)).start()

    app.run(debug=True, port=port, threaded=True)
