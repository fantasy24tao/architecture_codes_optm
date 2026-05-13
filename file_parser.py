import os
import io
from typing import Tuple
import fitz
import numpy as np
import easyocr
from PIL import Image
from docx import Document


class FileParser:
    def __init__(self, ocr_lang: str = 'ch_sim,en'):
        self.ocr_langs = [lang.strip() for lang in ocr_lang.split(',')]
        self._ocr_reader = None

    def _get_ocr_reader(self):
        if self._ocr_reader is None:
            self._ocr_reader = easyocr.Reader(self.ocr_langs)
        return self._ocr_reader

    def parse_txt(self, file_bytes: bytes) -> str:
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_bytes.decode('gbk')
            except UnicodeDecodeError:
                return file_bytes.decode('latin-1')

    def parse_pdf(self, file_bytes: bytes, use_ocr_fallback: bool = True) -> Tuple[str, bool]:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(page_text)
        
        extracted_text = '\n'.join(text_parts).strip()
        
        if len(extracted_text) > 100:
            return extracted_text, False
        
        if use_ocr_fallback:
            ocr_text = self._parse_pdf_with_ocr(doc)
            return ocr_text, True
        
        return extracted_text, False
            
    def _parse_pdf_with_ocr(self, doc):
        reader = self._get_ocr_reader()
        text_parts = []
        
        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                img_np = img_np[:, :, :3]
            results = reader.readtext(img_np, detail=0)
            page_text = '\n'.join(results)
            text_parts.append(f"[第 {page_num + 1} 页]\n{page_text}")
        
        return '\n'.join(text_parts)

    def parse_docx(self, file_bytes: bytes) -> str:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs]
        return '\n'.join(paragraphs)

    def parse_file(self, file_bytes: bytes, filename: str) -> Tuple[str, str]:
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if ext == 'txt':
            text = self.parse_txt(file_bytes)
            mode = "普通文本"
        elif ext == 'pdf':
            text, is_scanned = self.parse_pdf(file_bytes)
            mode = "扫描版PDF(OCR)" if is_scanned else "普通PDF"
        elif ext in ['doc', 'docx']:
            text = self.parse_docx(file_bytes)
            mode = "Word文档"
        else:
            raise Exception(f"不支持的文件格式: .{ext}")
        
        return text, mode
