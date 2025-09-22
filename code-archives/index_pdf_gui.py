import os
import json
from pathlib import Path
from datetime import datetime
from PyPDF2 import PdfReader
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import tkinter as tk
from tkinter import filedialog, messagebox

selected_folder = None

def extract_text_from_pdf_file(args):
    root_folder, relative_path = args
    pdf_path = os.path.join(root_folder, relative_path)
    try:
        reader = PdfReader(pdf_path)
        text = " ".join(page.extract_text() or "" for page in reader.pages)
        return (relative_path, text.lower() if text.strip() else None)
    except Exception:
        return (relative_path, None)

def write_log(log_path, msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {msg}\n")

def save_index(index_path, index_obj):
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_obj, f, indent=2, ensure_ascii=False)

def process_folder(pdf_root):
    index_folder = os.path.join(pdf_root, "index")
    os.makedirs(index_folder, exist_ok=True)
    index_path = os.path.join(index_folder, "index.json")
    log_path = os.path.join(index_folder, "index_log.txt")

    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {}

    pdf_files = [str(p.relative_to(pdf_root)) for p in Path(pdf_root).rglob("*.pdf")]
    pdf_files = [f for f in pdf_files if f not in index]
    total = len(pdf_files)

    if total == 0:
        messagebox.showinfo("Done", "✅ All PDF files are already indexed.")
        return

    num_cpus = multiprocessing.cpu_count()
    used_cpus = max(1, num_cpus // 2)
    print(f"⚙️ Indexing {total} files using {used_cpus}/{num_cpus} CPUs...")

    with ProcessPoolExecutor(max_workers=used_cpus) as executor:
        tasks = [(pdf_root, f) for f in pdf_files]
        futures = {executor.submit(extract_text_from_pdf_file, args): args[1] for args in tasks}
        for future in tqdm(as_completed(futures), total=total, desc="Indexing"):
            filename, result = future.result()
            if result:
                index[filename] = result
                write_log(log_path, f"✅ Indexed: {filename}")
            else:
                write_log(log_path, f"⚠️ Failed or empty: {filename}")

    save_index(index_path, index)
    write_log(log_path, f"[✔️] Finalized: {len(index)} indexed total")
    messagebox.showinfo("Done", f"[✔️] Finished: {len(index)} indexed total")

def select_folder():
    global selected_folder
    folder = filedialog.askdirectory(title="Select Folder with PDFs")
    if folder:
        selected_folder = folder
        folder_label.config(text=f"📂 {folder}", fg="green")

def start_indexing():
    if not selected_folder:
        messagebox.showwarning("Warning", "Please select a folder first!")
    else:
        process_folder(selected_folder)

def run_gui():
    global folder_label
    root = tk.Tk()
    root.title("📄 EMC PDF Indexer")

    tk.Label(root, text="Select the folder containing PDFs", font=("Arial", 12)).pack(pady=10)

    folder_label = tk.Label(root, text="📂 No folder selected", fg="red", font=("Arial", 10))
    folder_label.pack(pady=5)

    tk.Button(root, text="📁 Select Folder", command=select_folder, width=20, font=("Arial", 12)).pack(pady=5)
    tk.Button(root, text="📌 Index Now", command=start_indexing, width=20, font=("Arial", 12)).pack(pady=5)
    tk.Button(root, text="❌ Exit", command=root.destroy, width=20, font=("Arial", 12)).pack(pady=5)

    root.geometry("450x250")
    root.mainloop()

if __name__ == "__main__":
    run_gui()
