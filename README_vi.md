# 📑 Trình Lập Chỉ Mục PDF (Atomic JSON Index với Dọn Dẹp)

Công cụ này quét một thư mục (và các thư mục con) chứa các file PDF, trích xuất văn bản theo từng trang bằng [pdfplumber](https://github.com/jsvine/pdfplumber), và lưu kết quả vào file `index.json`.  

Đặc điểm nổi bật:
- **Gia tăng (Incremental)** → bỏ qua các file không thay đổi.  
- **An toàn (Atomic)** → cập nhật `index.json` không bị hỏng.  
- **Tự dọn dẹp** → xóa mục trong index nếu file PDF đã bị xóa hoặc di chuyển.  
- **Đa nền tảng** → chạy được trên Ubuntu, macOS và Windows 11.  

---

## 🚀 Tính năng
- Trích xuất văn bản theo từng trang từ PDF.  
- Ghi log chi tiết và lỗi trong quá trình chạy.  
- Lưu JSON với dấu thời gian chỉnh sửa.  
- Tự động xóa mục index khi file không còn tồn tại.  

---

## 🛠️ Cài đặt

### 1. Tải mã nguồn
```bash
git clone https://github.com/yourusername/pdf-indexer.git
cd pdf-indexer
```

### 2. Tạo môi trường Python
> Khuyến nghị dùng Python 3.9+.

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

### 3. Cài đặt thư viện cần thiết
Công cụ cần:  
- `pdfplumber` (đọc PDF)  
- `tqdm` (thanh tiến trình)  

Cài đặt bằng lệnh:
```bash
pip install pdfplumber tqdm
```

---

## ▶️ Sử dụng

### Lệnh cơ bản
Lập chỉ mục tất cả PDF trong thư mục mặc định (`../database/pdf-test`):
```bash
python index_pdf_1cpu_path_v1.py
```

### Chỉ định đường dẫn khác
```bash
python index_pdf_1cpu_path_v1.py --path="D:/Books/MyPDFs"
```

### File đầu ra
- `index.json` → dữ liệu JSON có trang & thời gian chỉnh sửa  
- `index_failed.txt` → log lỗi cho các file PDF không xử lý được  
- `index.log.txt` → log chi tiết quá trình chạy  

---

## 📂 Ví dụ kết quả JSON
```json
{
  "docs/sample.pdf": {
    "_mtime": 1726892310.0,
    "pages": [
      { "page": 1, "text": "Nội dung trang 1..." },
      { "page": 2, "text": "Nội dung trang 2..." }
    ]
  }
}
```

---

## 🧹 Tự động dọn dẹp
Nếu một file bị xóa hoặc di chuyển, mục tương ứng trong `index.json` sẽ bị xóa ở lần chạy tiếp theo.

---

## 📖 Giấy phép
MIT License. Miễn phí sử dụng và chỉnh sửa.
