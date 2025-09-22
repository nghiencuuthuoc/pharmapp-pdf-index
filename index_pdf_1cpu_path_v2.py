import os, json, tempfile
from datetime import datetime
import pdfplumber
from tqdm import tqdm
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

# --- Safe JSON helpers ---
def _backup_corrupt_index(src_path):
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = f"{src_path}.bad_{ts}.json"
        os.replace(src_path, dst)  # atomic rename
        return dst
    except Exception:
        return None

def _write_json_atomic(path, data):
    dir_ = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(prefix="index_", suffix=".tmp", dir=dir_)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)  # atomic on Windows & POSIX
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

def load_existing_index():
    if os.path.exists(INDEX_JSON):
        try:
            with open(INDEX_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Đảm bảo kiểu dict
                if not isinstance(data, dict):
                    raise json.JSONDecodeError("index.json must be an object", doc="", pos=0)
                return data
        except json.JSONDecodeError as e:
            bak = _backup_corrupt_index(INDEX_JSON)
            log_info(f"⚠️ index.json corrupt, backed up to {bak or '(backup failed)'}: {e}")
            return {}
    return {}

# --- NEW: prune stale entries that no longer exist on disk ---
def prune_stale_entries(index_data, current_rel_paths):
    if not isinstance(index_data, dict):
        return 0
    keep = set(current_rel_paths)
    # Chỉ xét các key là đường dẫn (bỏ qua field kỹ thuật nếu có)
    keys = [k for k in list(index_data.keys()) if isinstance(k, str) and not k.startswith("_")]
    stale = [k for k in keys if k not in keep]
    removed = 0
    for k in stale:
        del index_data[k]
        removed += 1
        log_info(f"🧹 Removed stale index: {k}")
    if removed:
        _write_json_atomic(INDEX_JSON, index_data)
    return removed

def index_all(folder):
    # 1) Quét danh sách PDF hiện có
    all_files = get_all_pdfs(folder)

    # 2) Nạp index hiện có (tự backup nếu hỏng)
    index_result = load_existing_index()

    # 3) DỌN RÁC: xóa các entry không còn file
    pruned = prune_stale_entries(index_result, all_files)

    indexed = skipped = updated = 0

    # 4) Index/Update theo mtime
    for rel_path in tqdm(all_files, desc="🔍 Indexing PDFs"):
        abs_path = os.path.join(folder, rel_path)

        # Lấy mtime an toàn
        try:
            file_mtime = os.path.getmtime(abs_path)
        except FileNotFoundError:
            # File vừa bị xoá/di chuyển giữa lúc chạy → bỏ qua; sẽ được prune ở vòng sau
            log_info(f"⏭️ Skipped (disappeared): {rel_path}")
            continue

        cached = index_result.get(rel_path)
        cached_mtime = cached.get("_mtime") if isinstance(cached, dict) else None
        if cached_mtime is not None and file_mtime <= cached_mtime:
            skipped += 1
            continue

        log_info(f"📌 Processing {rel_path}")
        content = index_single_pdf(rel_path)
        if content:
            index_result[rel_path] = {
                "_mtime": file_mtime,
                "pages": content
            }
            updated += 1
            # Ghi nguyên tử sau mỗi file để tránh mất dữ liệu
            _write_json_atomic(INDEX_JSON, index_result)
        else:
            log_error(rel_path, "No content or error during indexing.")
        indexed += 1

    return index_result, indexed, skipped, updated, pruned

# --- Main ---
if __name__ == "__main__":
    print(f"🚀 Starting PDF indexing in: {OCR_FOLDER}")
    os.makedirs(os.path.dirname(INDEX_JSON), exist_ok=True)

    result, total_indexed, total_skipped, total_updated, total_pruned = index_all(OCR_FOLDER)

    print(f"✅ Done. Indexed: {total_indexed} | Skipped: {total_skipped} | Updated: {total_updated} | Pruned: {total_pruned}")
    print(f"📁 Index saved → {INDEX_JSON}")
    print(f"📝 Error log → {ERROR_LOG}")
    print(f"📋 Detailed log → {DETAIL_LOG}")

# how_use
# python CP-2025_index_pdf.py
# python CP-2025_index_pdf.py --path="D:/Books/MyPDFs"
