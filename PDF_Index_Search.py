import json
import streamlit as st
from PIL import Image
import re
import os

def get_index_path(path):
    """Smartly resolve the index.json path, whether given a folder or a file path."""
    path = os.path.abspath(path)
    if path.lower().endswith('.json') and os.path.isfile(path):
        return path
    if os.path.isdir(path):
        return os.path.join(path, "index.json")
    if path.lower().endswith('.json'):  # allow for new json (not exist yet)
        return path
    raise ValueError(f"Path is neither a .json file nor a valid directory: {path}")

def highlight(text, keyword):
    if not keyword.strip():
        return text
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(lambda m: f'<mark style="background: #fff799">{m.group(0)}</mark>', text)

def display_name(item):
    m = re.search(r'page_(\d+)', item['filename'])
    page = m.group(1).lstrip("0") if m else "?"
    short_text = item["text"].strip().replace("\n", " ")[:60]
    return f"Picture | {short_text}..."

def run():
    st.set_page_config(page_title="PDF_Index_Search", layout="wide")
    st.title("📷 PDF_Index_Search")

    # Default input_path
    input_path = "E:/PDF_Files/index_image.json"
    index_path = get_index_path(input_path)
    folder = os.path.dirname(index_path)

    index_data = []
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    else:
        st.warning("Cannot find index.json in this folder. Please run the OCR script first.")

    # --- Giao diện tìm kiếm & Gallery ---
    if index_data:
        if 'clicked_idx' not in st.session_state:
            st.session_state['clicked_idx'] = None
        if 'keyword' not in st.session_state:
            st.session_state['keyword'] = ''

        keyword = st.text_input("🔎 Search keyword", value=st.session_state.get('keyword', ''))
        if keyword:
            # Lọc các ảnh còn tồn tại thật sự trên ổ cứng
            filtered_results = []
            for item in index_data:
                if keyword.lower() in item['text'].lower():
                    img_path = os.path.join(folder, item["filename"])
                    if os.path.exists(img_path):
                        filtered_results.append(item)
            results = filtered_results

            st.write(f"Found **{len(results)}** image(s) containing keyword: `{keyword}`")
            if len(results) == 0:
                st.info("No images found.")
            else:
                cols = st.columns(5)
                for idx, item in enumerate(results):
                    img_path = os.path.join(folder, item["filename"])
                    with cols[idx % 5]:
                        if st.button("", key=f"img-btn-{idx}"):
                            st.session_state['clicked_idx'] = idx
                            st.session_state['keyword'] = keyword
                        st.image(img_path, use_container_width=True, caption=f"{item['filename'][:40]}")
                clicked_idx = st.session_state.get('clicked_idx', None)
                if clicked_idx is not None and clicked_idx < len(results):
                    img_item = results[clicked_idx]
                    img_path = os.path.join(folder, img_item["filename"])
                    st.subheader(f"Detail view: {img_item['filename']}")
                    st.image(img_path, use_container_width=True)
                    highlighted = highlight(img_item["text"][:2000], keyword)
                    st.markdown(highlighted, unsafe_allow_html=True)
                    if st.button("Clear selection"):
                        st.session_state['clicked_idx'] = None

    # --- FOOTER ---
    st.markdown("""<br><hr><div style='text-align:center; font-size: 12px'>
    | Copyright 2025 | 🧠 Nghiên Cứu Thuốc | PharmApp |<br>
    | Discover | Design | Optimize | Create | Deliver | <br>
    | www.nghiencuuthuoc.com | Zalo: +84888999311 | www.pharmapp.vn |
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    run()
