from flask import Flask, render_template, request, send_file
import qrcode
from qrcode.image.pil import PilImage  # Explicitly import Pillow supportimport qrcode
import qrcode.image.styles.moduledrawers as md
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', qr_code=None)

@app.route('/qrcode', methods=['POST'])
def generate_qr():
    qr_type = request.form.get('type', 'link').lower()
    file_format = request.form.get('format', 'png').lower()
    style = request.form.get('style', 'square').lower()

    # Handle data input
    if qr_type == 'link':
        data = request.form.get('data', '')
    elif qr_type == 'contact':
        name = request.form.get('name', 'John Doe')
        phone = request.form.get('phone', '+1234567890')
        email = request.form.get('email', 'example@email.com')
        org = request.form.get('org', 'My Company')
        data = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
ORG:{org}
TEL:{phone}
EMAIL:{email}
END:VCARD"""
    else:
        return "Invalid type", 400

    # Choose module drawer (style)
    if style == 'rounded':
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(image_factory=qrcode.image.pil.PilImage, module_drawer=md.RoundedModuleDrawer())
    else:
        qr = qrcode.make(data)
        img = qr

    buffer = io.BytesIO()
    if file_format == 'png':
        img.save(buffer, format="PNG")
        mimetype = 'image/png'
        extension = 'png'
    elif file_format == 'svg':
        img.save(buffer, format="SVG")
        mimetype = 'image/svg+xml'
        extension = 'svg'
    else:
        return "Invalid format", 400

    buffer.seek(0)
    encoded_qr = base64.b64encode(buffer.getvalue()).decode()

    return render_template('index.html', qr_code=encoded_qr, format=file_format, extension=extension, data=data)

@app.route('/download/<file_format>')
def download_qr(file_format):
    data = request.args.get('data', '')
    qr = qrcode.make(data)
    buffer = io.BytesIO()

    if file_format == 'png':
        qr.save(buffer, format="PNG")
        mimetype = 'image/png'
        filename = "qrcode.png"
    elif file_format == 'svg':
        qr.save(buffer, format="SVG")
        mimetype = 'image/svg+xml'
        filename = "qrcode.svg"
    else:
        return "Invalid format", 400

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, mimetype=mimetype, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
