from flask import Flask, request, render_template, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename

# Base directory (fix path issues)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask app
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

# Folders
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
CLEAN_FOLDER = os.path.join(BASE_DIR, "cleaned")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEAN_FOLDER, exist_ok=True)

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('user_inter.html')


# ---------------- UPLOAD + CLEAN ----------------
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')

    # Validation
    if file is None or file.filename == '':
        return render_template('user_inter.html', error="⚠️ No file selected")

    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        return render_template('user_inter.html', error="⚠️ Only CSV or Excel files allowed")

    try:
        # Secure filename
        filename = secure_filename(file.filename)

        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Read file
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # -------- DATA CLEANING --------
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        # Check if empty after cleaning
        if df.empty:
            return render_template('user_inter.html', error="⚠️ No data left after cleaning")

        # Save cleaned file
        clean_path = os.path.join(CLEAN_FOLDER, "cleaned_data.csv")
        df.to_csv(clean_path, index=False)

        # Preview
        table = df.head().to_html(classes='table table-bordered', index=False)

        return render_template(
            'user_inter.html',
            tables=table,
            success="✅ File processed successfully!"
        )

    except Exception as e:
        return render_template('user_inter.html', error=f"⚠️ Error: {str(e)}")


# ---------------- DOWNLOAD ----------------
@app.route('/download')
def download():
    path = os.path.join(CLEAN_FOLDER, "cleaned_data.csv")

    if not os.path.exists(path):
        return "⚠️ File not found. Please upload and process a file first."

    return send_file(path, as_attachment=True)


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
