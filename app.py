
from flask import Flask, render_template, request, send_file
import qrcode
from qrcode.image.pil import PilImage
from PIL import Image
import os
from datetime import datetime
import user_agents

app = Flask(__name__)

# Ensure 'static' folder exists for storing QR codes
if not os.path.exists("static"):
    os.makedirs("static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_qr():
    qr_type = request.form.get("qr_type")
    data = request.form.get("data")
    qr_color = request.form.get("qr_color", "#000000")
    logo = request.files.get("logo")

    if not data:
        return "No data provided!", 400

    if qr_type == "vcf":
        data = f"BEGIN:VCARD\nFN:{data}\nEND:VCARD"

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=qr_color, back_color="white")

    # Add logo if provided
    if logo:
        logo_path = "static/logo.png"
        logo.save(logo_path)
        img = img.convert("RGBA")
        logo_img = Image.open(logo_path)
        
        # Resize logo
        logo_size = (img.size[0] // 4, img.size[1] // 4)
        logo_img = logo_img.resize(logo_size, Image.ANTIALIAS)

        # Paste logo at center
        pos = ((img.size[0] - logo_size[0]) // 2, (img.size[1] - logo_size[1]) // 2)
        img.paste(logo_img, pos, logo_img)

    qr_path = "static/qr-code.png"
    img.save(qr_path)

    return qr_path

@app.route("/download/<format>")
def download_qr(format):
    qr_path = "static/qr-code.png"
    if format == "svg":
        qr_path = "static/qr-code.svg"
    return send_file(qr_path, as_attachment=True)


# Dashboard

LOG_FILE = "visitor_log.txt"


def get_device_type(user_agent_string):
    """Detects if visitor is using a PC, Tablet, or Mobile."""
    ua = user_agents.parse(user_agent_string)
    if ua.is_mobile:
        return "Mobile"
    elif ua.is_tablet:
        return "Tablet"
    else:
        return "PC"


def log_ip():
    """Logs visitor IP, time, and device type."""
    user_ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device_type = get_device_type(request.headers.get("User-Agent", ""))

    log_entry = f"{timestamp},{user_ip},{device_type}\n"

    # Append log entry
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)


def read_logs():
    """Reads logs and returns a structured list."""
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    logs = [line.strip().split(",") for line in lines]
    return logs[::-1]  # Show newest logs first


@app.route("/")
def home():
    log_ip()  # Log visitor's details
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/get_logs")
def get_logs():
    """Returns logs as JSON for dynamic table update."""
    logs = read_logs()
    total_visitors = len(logs)
    return jsonify({"logs": logs, "total": total_visitors})


if __name__ == "__main__":
    app.run(debug=True)
