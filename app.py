from flask import Flask, request, render_template, send_file, url_for
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
from pyngrok import ngrok

app = Flask(__name__)

# Directories for image storage
UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/output"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Start ngrok tunnel
public_url = ngrok.connect(5000)
print("Public URL:", public_url)

@app.route("/")
def home():
    return render_template("index.html", filename=None, enhanced=None)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    # Save the original image
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Process and enhance the image
    enhanced_filename = "enhanced_" + filename
    enhanced_path = enhance_image(filepath, enhanced_filename)

    return render_template("index.html", 
                           filename=url_for('static', filename=f'uploads/{filename}'), 
                           enhanced=url_for('static', filename=f'output/{enhanced_filename}'))

def enhance_image(image_path, enhanced_filename):
    img = cv2.imread(image_path)

    # Apply contrast and brightness enhancement
    alpha = 1.5  # Contrast
    beta = 20    # Brightness
    enhanced_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    output_path = os.path.join(app.config["OUTPUT_FOLDER"], enhanced_filename)
    cv2.imwrite(output_path, enhanced_img)
    return output_path

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(app.config["OUTPUT_FOLDER"], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(port=5000)
