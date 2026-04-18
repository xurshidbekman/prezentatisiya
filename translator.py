import os
import google.generativeai as genai
from PIL import Image

def init_translator():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY topilmadi!")
    genai.configure(api_key=api_key)

def translate_to_latex(input_data: str, is_image: bool = True) -> str:
    """
    Rasmni o'qib yoki matnni o'qib, fizikaga oid o'zbek tiliga tarjima qilib, 
    LaTeX kodini qaytaradi.
    """
    # Gemini modelini sozlash
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    prompt = """
Siz professional fizika o'qituvchisi va tarjimonsiz. Ushbu ma'lumotlarda fizika bo'yicha matn, masalalar va formulalar tasvirlangan. 
Sizning vazifangiz:
1. Barcha yozuvlarni/matnlarni o'zbek tiliga to'g'ri va ilmiy tilda tarjima qilish (yoki tartiblash).
2. Matematik/fizik formulalarni aynan o'ziday qilib saqlab qolish.
3. Javoblarni LaTeX formatida kod sifatida yozib berish. 

Qoidalar:
- Formulalarni LaTeX da yozishda dollar belgilari ($...$ yoki $$...$$) yoki equation muhitidan foydalaning.
- HECH QANDAY preamblelar keragi yo'q (masalan, \\documentclass, \\begin{document} va hk. keragi YO'Q). Faqat matn va ichidagi formulalarni bering.
- Eng muhimi tarjima aniq, ravon o'zbek tilida bo'lsin.
    """

    if is_image:
        img = Image.open(input_data)
        response = model.generate_content([prompt, img])
    else:
        response = model.generate_content([prompt, input_data])
    
    # Javobni tozalash
    latex_text = response.text
    if latex_text.startswith("```latex"):
        latex_text = latex_text[8:]
    if latex_text.startswith("```"):
        latex_text = latex_text[3:]
    if latex_text.endswith("```"):
        latex_text = latex_text[:-3]

    return latex_text.strip()
