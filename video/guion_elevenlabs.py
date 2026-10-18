"""Genera el guion de locución para ElevenLabs en Word (video/out/Guion-ElevenLabs-FactoryMind.docx)."""
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm

NAVY = RGBColor(0x0B, 0x1E, 0x33)
GREEN = RGBColor(0x1E, 0x9E, 0x5A)
GREY = RGBColor(0x5A, 0x64, 0x73)

SCENES = [
    ("1", "El problema", "00:00 – 00:05", "5 s",
     "Cinco operarios, una misma línea… pero cada puesto trabaja a un ritmo diferente."),
    ("2", "El cuello de botella", "00:05 – 00:12", "7 s",
     "Un cuello de botella de treinta segundos provoca acumulaciones, esperas y pérdidas de productividad."),
    ("3", "Entra Factory Mind", "00:12 – 00:18", "6 s",
     "Factory Mind analiza los tiempos, identifica las pérdidas y estudia cómo equilibrar las operaciones."),
    ("4", "Rediseñamos la línea", "00:18 – 00:25", "7 s",
     "Redistribuimos las tareas, eliminamos esperas y definimos una nueva secuencia de trabajo. Sin añadir personal."),
    ("5", "El después", "00:25 – 00:34", "9 s",
     "Ahora cada puesto trabaja al ritmo de la línea. Menos esperas, menos acumulaciones y un flujo mucho más eficiente."),
    ("6", "El resultado", "00:34 – 00:42", "8 s",
     "El resultado: una capacidad potencial un cincuenta por ciento superior, aprovechando mejor los mismos recursos."),
    ("7", "Cierre", "00:42 – 00:48", "6 s",
     "Factory Mind. La productividad no consiste en trabajar más rápido, sino en trabajar mejor."),
]

# Pausas entre escenas para el bloque único, ajustadas a un ritmo de unas 2,6 palabras/s
BREAKS = ["0.6s", "0.8s", "0.6s", "0.8s", "0.8s", "1.0s"]


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def heading(doc, text, size=14, color=NAVY, space_before=14):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(size)
    r.font.color.rgb = color
    return p


def body(doc, text, color=None, italic=False, size=10.5):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.italic = italic
    if color:
        r.font.color.rgb = color
    return p


def paste_box(doc, text):
    """Cuadro sombreado con el texto exacto a pegar en ElevenLabs."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    shade(c, "EEF5F0")
    c.paragraphs[0].text = ""
    r = c.paragraphs[0].add_run(text)
    r.font.name = "Consolas"
    r.font.size = Pt(10.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def main():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.2)
        s.top_margin = s.bottom_margin = Cm(2)

    p = doc.add_paragraph()
    r = p.add_run("FACTORY MIND | ANTES Y DESPUÉS")
    r.bold = True
    r.font.size = Pt(20)
    r.font.color.rgb = NAVY
    p = doc.add_paragraph()
    r = p.add_run("Guion de locución para ElevenLabs · «El poder de equilibrar una línea de producción»")
    r.font.size = Pt(12)
    r.font.color.rgb = GREEN
    body(doc, "Duración total: 48 s · 16:9 · Locución en español de España · 7 escenas", GREY)

    # ------------------------------------------------------------------ ajustes
    heading(doc, "1. Ajustes recomendados en ElevenLabs")
    settings = [
        ("Modelo", "Eleven Multilingual v2 (o Eleven v3 si quieres más expresividad)"),
        ("Idioma / acento", "Español (España)"),
        ("Voz", "Masculina o femenina, registro corporativo, grave-media, ritmo firme. "
                "Busca en la Voice Library con «Spanish Spain narrator» o «documentary»."),
        ("Stability", "50 %"),
        ("Similarity", "75 %"),
        ("Style exaggeration", "10–15 %"),
        ("Speaker boost", "Activado"),
        ("Speed", "1,00 (si una escena se pasa de tiempo, baja a 1,05–1,10)"),
        ("Formato de descarga", "MP3 44,1 kHz 192 kbps o WAV"),
    ]
    t = doc.add_table(rows=0, cols=2)
    t.style = "Table Grid"
    for k, v in settings:
        row = t.add_row().cells
        row[0].text, row[1].text = k, v
        row[0].paragraphs[0].runs[0].bold = True
        shade(row[0], "E8EEF5")
        row[0].width, row[1].width = Cm(4.5), Cm(12)

    heading(doc, "Pronunciación de «Factory Mind»", 11, NAVY, 10)
    body(doc, "Si la voz lo lee a la española («fac-to-ri mind»), sustituye en el texto «Factory Mind» por "
              "«Fáctori Máind». No cambies nada más.")

    # ------------------------------------------------------------------ opción A
    heading(doc, "2. Opción A (recomendada): una toma por escena")
    body(doc, "Genera cada bloque por separado y descárgalo con el nombre indicado (VO_E1.mp3 … VO_E7.mp3). "
              "Así encajo cada frase exactamente en su escena del vídeo.")
    for n, title, tc, dur, txt in SCENES:
        words = len(txt.split())
        heading(doc, f"Escena {n} · {title}   |   {tc}   |   {dur}", 11, NAVY, 10)
        body(doc, f"Archivo: VO_E{n}.mp3   ·   {words} palabras   ·   duración máxima de la toma: {dur}",
             GREY, italic=True, size=9.5)
        paste_box(doc, txt)

    # ------------------------------------------------------------------ opción B
    heading(doc, "3. Opción B: bloque único con pausas")
    body(doc, "Copia todo el bloque y pégalo de una vez. Las etiquetas <break> generan los silencios entre escenas "
              "(funcionan en Multilingual v2; en Eleven v3 bórralas y deja solo los saltos de línea). "
              "Comprueba que el audio final dura entre 46 y 48 s.")
    lines = []
    for i, (_, _, _, _, txt) in enumerate(SCENES):
        lines.append(txt)
        if i < len(BREAKS):
            lines.append(f'<break time="{BREAKS[i]}" />')
    paste_box(doc, "\n".join(lines))

    # ------------------------------------------------------------------ tabla de sincronía
    heading(doc, "4. Tabla de sincronía con el vídeo")
    t = doc.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    hdr = ["Escena", "Tiempo", "Locución", "Rótulo en pantalla"]
    onscreen = [
        "ANTES | LÍNEA DESEQUILIBRADA",
        "P1 15 s · P2 19 s · P3 30 s · P4 12 s · P5 14 s / CUELLO DE BOTELLA 30 s / 120 bandejas/h",
        "FACTORY MIND · ANÁLISIS · CRONOMETRAJE · EQUILIBRADO",
        "EQUILIBRADO OPTIMIZADO · CICLO 30 s → 20 s",
        "DESPUÉS | FLUJO EQUILIBRADO",
        "+50 % CAPACIDAD · MISMO PERSONAL · MEJOR ORGANIZACIÓN",
        "FACTORY MIND · Más productividad. Mismos recursos.",
    ]
    for i, h in enumerate(hdr):
        c = t.rows[0].cells[i]
        c.text = h
        c.paragraphs[0].runs[0].bold = True
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(c, "0B1E33")
    for (n, title, tc, _, txt), ons in zip(SCENES, onscreen):
        row = t.add_row().cells
        row[0].text, row[1].text, row[2].text, row[3].text = f"{n}. {title}", tc, txt, ons
        for c in row:
            for r in c.paragraphs[0].runs:
                r.font.size = Pt(9)
    for row in t.rows:
        for c, w in zip(row.cells, (Cm(3), Cm(2.6), Cm(6.4), Cm(5))):
            c.width = w

    heading(doc, "5. Siguiente paso")
    body(doc, "Sube los MP3 a la carpeta video/audio/ del repositorio (o envíalos por el chat). "
              "Los monto sobre el vídeo, ajusto los tiempos de cada escena y, si quieres, añado una base musical "
              "por debajo de la voz.")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "Guion-ElevenLabs-FactoryMind.docx")
    doc.save(out)
    print(out)


if __name__ == "__main__":
    main()
