import os
import subprocess
import shutil

LATEX_PREAMBLE = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath, amsthm, amssymb, amsfonts}
\usepackage[uzbek]{babel}
\usepackage{geometry}
\geometry{a4paper, margin=2cm}

\begin{document}

"""

LATEX_POSTAMBLE = r"""

\end{document}
"""

def create_pdf(latex_content: str, output_name: str = "natija") -> tuple[str, str]:
    """
    Berilgan LaTeX kodiga preamble qoshib .tex fayl yasaydi 
    va pdflatex orqali pdf yaratadi.
    .tex va .pdf fayllari manzillarini (paths) qaytaradi.
    """
    tex_filename = f"{output_name}.tex"
    pdf_filename = f"{output_name}.pdf"
    
    full_latex = LATEX_PREAMBLE + latex_content + LATEX_POSTAMBLE
    
    # yozish
    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(full_latex)
    
    # PDF ga o'girish pdflatex orqali
    # -interaction=nonstopmode orqali xatolik bo'lsa to'xtab qolmasligini ta'minlaymiz
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_filename],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print("LaTeX da PDF generatsiya qilishda qisman xato bo'lishi mumkin, lekin pdf yasalgan bo'lishi ehtimoli bor.")
    except Exception as e:
        print(f"Boshqa xato: {e}")
        
    return tex_filename, pdf_filename
