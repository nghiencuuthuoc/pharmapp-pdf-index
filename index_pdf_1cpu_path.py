import os
import json
import pdfplumber
from tqdm import tqdm
from datetime import datetime
import argparse

# --- Argument Parser ---
parser = argparse.ArgumentParser(description="Index PDF files and extract page-level text.")
parser.add_argument(
    '--path',
    type=str,
    default="../database/pdf-test",
    help='Path to the folder containing PDFs (default: ../database/pdf-test)'
)
args = parser.parse_args()

# --- Dynamic Paths ---
OCR_FOLDER = os.path.abspath(args.path)
INDEX_JSON = os.path.join(OCR_FOLDER, "index.json")
ERROR_LOG = os.path.join(OCR_FOLDER, "index_failed.txt")
DETAIL_LOG = os.path.join(OCR_FOLDER, "index.log.txt")

# --- Utility functions ---
def get_all_pdfs(folder):
    pdf_files = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".pdf"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, OCR_FOLDER)
                pdf_files.append(rel_path)
    return pdf_files

def log_error(file_path, error_message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ❌ {file_path}: {error_message}\n")

def log_info(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DETAIL_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def index_single_pdf(rel_path):
    abs_path = os.path.join(OCR_FOLDER, rel_path)
    page_data = []

    try:
        with pdfplumber.open(abs_path) as pdf:
            for i, page in enumerate(tqdm(pdf.pages, desc=f"📄 {rel_path}", leave=False), start=1):
                text = page.extract_text()
                if text:
                    page_data.append({"page": i, "text": text.strip()})
        return page_data
    except Exception as e:
        log_error(rel_path, str(e))
        return None

def load_existing_index():
    if os.path.exists(INDEX_JSON):
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def index_all(folder):
    all_files = get_all_pdfs(folder)
    index_result = load_existing_index()
    indexed = 0
    skipped = 0
    updated = 0

    for rel_path in tqdm(all_files, desc="🔍 Indexing PDFs"):
        abs_path = os.path.join(folder, rel_path)

        if rel_path in index_result:
            last_indexed_time = os.path.getmtime(INDEX_JSON)
            file_mod_time = os.path.getmtime(abs_path)
            if file_mod_time <= last_indexed_time:
                skipped += 1
                continue

        log_info(f"📌 Processing {rel_path}")
        content = index_single_pdf(rel_path)
        if content:
            index_result[rel_path] = content
            updated += 1

            # ✅ Save after each successful indexing
            with open(INDEX_JSON, "w", encoding="utf-8") as f:
                json.dump(index_result, f, indent=2, ensure_ascii=False)
        else:
            log_error(rel_path, "No content or error during indexing.")
        indexed += 1

    return index_result, indexed, skipped, updated

# --- Main ---
if __name__ == "__main__":
    print(f"🚀 Starting PDF indexing in: {OCR_FOLDER}")
    os.makedirs(os.path.dirname(INDEX_JSON), exist_ok=True)

    result, total_indexed, total_skipped, total_updated = index_all(OCR_FOLDER)

    print(f"✅ Done. Indexed: {total_indexed} | Skipped: {total_skipped} | Updated: {total_updated}")
    print(f"📁 Index saved → {INDEX_JSON}")
    print(f"📝 Error log → {ERROR_LOG}")
    print(f"📋 Detailed log → {DETAIL_LOG}")



# how_use
# python CP-2025_index_pdf.py
# python CP-2025_index_pdf.py --path="D:/Books/MyPDFs"
