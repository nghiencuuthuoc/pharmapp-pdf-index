# 📑 PDF Indexer (Atomic JSON Index with Cleanup)

This tool scans a folder (and subfolders) of PDF files, extracts page-level text using [pdfplumber](https://github.com/jsvine/pdfplumber), and saves the results into an `index.json`.  

It is designed to be:
- **Incremental** → skips re-indexing if a file is unchanged.  
- **Atomic** → updates `index.json` safely (never corrupts).  
- **Self-cleaning** → removes orphaned entries when PDFs are deleted or moved.  
- **Cross-platform** → runs on Ubuntu, macOS, and Windows 11.  

---

## 🚀 Features
- Extracts text per-page from PDFs.  
- Logs detailed processing and errors.  
- Maintains a JSON index with modification timestamps.  
- Automatically prunes missing files from the index.  

---

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/pdf-indexer.git
cd pdf-indexer
```

### 2. Create Python Environment
> Python 3.9+ recommended.

#### Ubuntu / macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows 11 (PowerShell)
```powershell
python -m venv venv
.env\Scriptsctivate
pip install -r requirements.txt
```

### 3. Install Dependencies
The script needs:
- `pdfplumber` (PDF parsing)
- `tqdm` (progress bar)

Install via:
```bash
pip install pdfplumber tqdm
```

---

## ▶️ Usage

### Basic Command
Index all PDFs in the default folder (`../database/pdf-test`):
```bash
python index_pdf_1cpu_path_v1.py
```

### Custom Path
```bash
python index_pdf_1cpu_path_v1.py --path="D:/Books/MyPDFs"
```

### Outputs
- `index.json` → structured JSON index with pages & timestamps  
- `index_failed.txt` → error log for problematic PDFs  
- `index.log.txt` → detailed processing logs  

---

## 📂 Example JSON Output
```json
{
  "docs/sample.pdf": {
    "_mtime": 1726892310.0,
    "pages": [
      { "page": 1, "text": "First page text..." },
      { "page": 2, "text": "Second page text..." }
    ]
  }
}
```

---

## 🧹 Auto-Cleanup
If a file is deleted or moved, its entry in `index.json` is automatically removed during the next run.

---

## 📖 License
MIT License. Free to use and modify.
