@echo off
mode con: cols=95 lines=20
color A1
@echo on
@ Echo: +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@ Echo: PharmApp // Copyright 2025 // NGHIEN CUU THUOC // RnD PHARMA PLUS // WWW.NGHIENCUUTHUOC.COM
@ Echo: Email: nghiencuuthuoc@gmail.com // LinkedIN: https://linkedin.com/in/nghiencuuthuoc
@ Echo: YouTube: https://youtube.com/@nghiencuuthuoc // Twitter: https://x.com/nghiencuuthuoc 
@ Echo: Zalo: +84888999311 // WhatsAapp: +84888999311 // Facebook: https://fb.com/nghiencuuthuoc
@ Echo: +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@echo off
Title pdfi1

REM === Prompt for input path ===
set /p PDF_PATH=Enter the folder path to index PDF files: 

REM === Activate virtual environment ===
call E:\DrugDev\NCT-App\pdf-tools\venv-ocr\Scripts\activate

Title PDF Indexer // "%PDF_PATH%"
REM === Run the PDF indexing script ===
python index_pdf_1cpu_path_v1.py --path="%PDF_PATH%"

echo        DONE! Check your logs and index.json in the specified folder.
pause
cls
index_pdf_1cpu_path_v1.bat