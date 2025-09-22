import os
import json
import time
from pathlib import Path
from datetime import datetime
from PyPDF2 import PdfReader
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
from PIL import Image, ImageTk
import requests
from io import BytesIO

selected_folder = None

LOGO_URL = "https://raw.githubusercontent.com/nghiencuuthuoc/PharmApp/refs/heads/master/images/nct_logo_3000x3000_20250606.png"
LOGO_PATH = os.path.join("assets", "nct_logo.png")

def ensure_logo():
    os.makedirs("assets", exist_ok=True)
    if not os.path.exists(LOGO_PATH):
        try:
            response = requests.get(LOGO_URL)
            with open(LOGO_PATH, "wb") as f:
                f.write(response.content)
            print("✅ Logo downloaded and saved.")
        except Exception as e:
            print(f"❌ Failed to download logo: {e}")

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

def format_eta(seconds_left):
    if seconds_left < 60:
        return f"{int(seconds_left)}s"
    elif seconds_left < 3600:
        return f"{int(seconds_left // 60)}m {int(seconds_left % 60)}s"
    else:
        h = seconds_left // 3600
        m = (seconds_left % 3600) // 60
        s = seconds_left % 60
        return f"{int(h)}h {int(m)}m {int(s)}s"

def process_folder(pdf_root, progress_var, progress_bar, eta_label):
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

    start_time = time.time()

    with ProcessPoolExecutor(max_workers=used_cpus) as executor:
        tasks = [(pdf_root, f) for f in pdf_files]
        futures = {executor.submit(extract_text_from_pdf_file, args): args[1] for args in tasks}
        completed = 0
        for future in as_completed(futures):
            filename, result = future.result()
            if result:
                index[filename] = result
                write_log(log_path, f"✅ Indexed: {filename}")
            else:
                write_log(log_path, f"⚠️ Failed or empty: {filename}")
            completed += 1
            elapsed = time.time() - start_time
            avg_time = elapsed / completed
            remaining = (total - completed) * avg_time
            eta_label.config(text=f"⏳ ETA: {format_eta(remaining)}")
            progress = int((completed / total) * 100)
            progress_var.set(progress)
            progress_bar.update()

    save_index(index_path, index)
    write_log(log_path, f"[✔️] Finalized: {len(index)} indexed total")
    eta_label.config(text="✅ Done.")
    messagebox.showinfo("Done", f"[✔️] Finished: {len(index)} indexed total")

def threaded_indexing(progress_var, progress_bar, eta_label):
    if not selected_folder:
        messagebox.showwarning("Warning", "Please select a folder first!")
    else:
        t = Thread(target=process_folder, args=(selected_folder, progress_var, progress_bar, eta_label))
        t.start()

def select_folder(label):
    global selected_folder
    folder = filedialog.askdirectory(title="Select Folder with PDFs")
    if folder:
        selected_folder = folder
        label.config(text=f"📂 {folder}", fg="green")

def run_gui():
    ensure_logo()

    root = tk.Tk()
    root.title("📄 EMC PDF Indexer")

    # Logo display
    try:
        logo_img = Image.open(LOGO_PATH).resize((160, 160))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(root, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.pack(pady=5)
    except Exception as e:
        tk.Label(root, text="(Logo not found or failed)", fg="red").pack()

    tk.Label(root, text="Select the folder containing PDFs", font=("Arial", 12)).pack(pady=5)

    folder_label = tk.Label(root, text="📂 No folder selected", fg="red", font=("Arial", 10))
    folder_label.pack(pady=5)

    tk.Button(root, text="📁 Select Folder", command=lambda: select_folder(folder_label), width=20, font=("Arial", 12)).pack(pady=5)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=progress_var)
    progress_bar.pack(pady=10)

    eta_label = tk.Label(root, text="⏳ ETA: ...", font=("Arial", 10), fg="blue")
    eta_label.pack(pady=5)

    tk.Button(root, text="📌 Index Now", command=lambda: threaded_indexing(progress_var, progress_bar, eta_label), width=20, font=("Arial", 12)).pack(pady=5)
    tk.Button(root, text="❌ Exit", command=root.destroy, width=20, font=("Arial", 12)).pack(pady=5)

    # Footer
    tk.Label(root, text="| Copyright 2025 | 🥣 Nghiên Cứu Thuốc | 🧠 PharmApp |", font=("Arial", 9)).pack(pady=(20, 0))
    tk.Label(root, text="| Discover | Design | Optimize | Create | Deliver |", font=("Arial", 9)).pack()
    tk.Label(root, text="| www.nghiencuuthuoc.com | Zalo: +84888999311 |", font=("Arial", 9)).pack()

    root.geometry("560x530")
    root.mainloop()

if __name__ == "__main__":
    run_gui()
