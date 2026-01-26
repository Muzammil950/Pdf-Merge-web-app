from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfMerger
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        merger = PdfMerger()
        files = request.files.getlist("pdfs")

        for file in files:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)
            merger.append(path)

        output = os.path.join(UPLOAD_FOLDER, "merged.pdf")
        merger.write(output)
        merger.close()

        return send_file(output, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
