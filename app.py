from flask import Flask, render_template, request, send_file, flash, redirect
from PyPDF2 import PdfMerger
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        files = request.files.getlist("files")

        if not files or files[0].filename == "":
            flash("Please upload at least one file.")
            return redirect(request.url)

        merger = PdfMerger()
        saved_files = []

        for file in files:
            if file and allowed_file(file.filename):

                filename = secure_filename(file.filename)
                unique_name = str(uuid.uuid4()) + "_" + filename
                path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
                file.save(path)

                ext = filename.rsplit(".", 1)[1].lower()

                # 🔹 If Image → Convert to PDF
                if ext in {"jpg", "jpeg", "png"}:
                    image = Image.open(path)
                    pdf_path = path + ".pdf"
                    image.convert("RGB").save(pdf_path)
                    merger.append(pdf_path)
                    saved_files.append(pdf_path)
                else:
                    merger.append(path)

                saved_files.append(path)

            else:
                flash("Only PDF or Image files allowed.")
                return redirect(request.url)

        output_filename = str(uuid.uuid4()) + "_merged.pdf"
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

        merger.write(output_path)
        merger.close()

        # Clean temp files
        for f in saved_files:
            if os.path.exists(f):
                os.remove(f)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
