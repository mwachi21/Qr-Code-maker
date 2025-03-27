
from flask import Flask, render_template, request, send_file
import qrcode
from qrcode.image.pil import PilImage
from PIL import Image
import os

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

if __name__ == "__main__":
    app.run(debug=True)
