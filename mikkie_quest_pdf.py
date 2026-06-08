#!/usr/bin/env python3
"""MIKKIE WORLD Quest PDF Generator — maakt een gratis leadmagnet PDF"""
import os, sys

try:
    from fpdf import FPDF
except ImportError:
    os.system('pip3 install fpdf2 -q')
    from fpdf import FPDF

QUESTS = [
    ("Missie 1: De Steenjager", "Zoek een steen die op een dier lijkt. Teken hem na op dit blad. Geef hem een naam!"),
    ("Missie 2: De Boomhutbouwer", "Bouw een mini-huisje van takjes en bladeren. Wie woont erin? Teken de bewoner!"),
    ("Missie 3: De Vogelluisteraar", "Ga buiten staan en luister. Hoeveel verschillende vogels hoor je? Schrijf ze op!"),
    ("Missie 4: De Regenboogmaker", "Maak een regenboog met krijtjes op de stoep. Elke kleur is een wens. Wat wens jij?"),
    ("Missie 5: De Miniatuurontdekker", "Zoek iets in de tuin dat kleiner is dan je pink. Wat vind je? Teken het!"),
    ("Missie 6: De Boomrenner", "Ren zo snel als je kan naar de dichtstbijzijnde boom en terug. Laat iemand je tijd opnemen!"),
    ("Missie 7: De Dierenimitator", "Maak het geluid van 3 verschillende dieren. Welk dier ben jij vandaag?"),
]

COLORS = {
    'blue': (59, 130, 246),
    'yellow': (245, 158, 11),
    'green': (34, 197, 94),
    'orange': (251, 146, 60),
    'purple': (139, 92, 246),
    'red': (239, 68, 68),
    'pink': (236, 72, 153),
}

COLOR_LIST = list(COLORS.values())

def create_pdf(output_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Cover page
    pdf.add_page()
    r, g, b = 59, 130, 246
    pdf.set_fill_color(r, g, b)
    pdf.rect(0, 0, 210, 297, 'F')

    pdf.set_fill_color(245, 158, 11)
    pdf.rect(10, 10, 190, 277, 'F')

    pdf.set_fill_color(255, 255, 255)
    pdf.rect(15, 15, 180, 267, 'F')

    pdf.set_font('Helvetica', 'B', 36)
    pdf.set_text_color(59, 130, 246)
    pdf.set_y(40)
    pdf.cell(0, 20, 'MIKKIE WORLD', align='C', ln=True)

    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, '7 Gratis Buitenmissies', align='C', ln=True)

    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.ln(10)
    pdf.cell(0, 10, 'Voor avonturiers van 4 tot 12 jaar', align='C', ln=True)

    pdf.ln(20)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, 'Waar Elk Kind een Held Is', align='C', ln=True)

    pdf.ln(10)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'Launch: 7 juli 2026 om 07:07', align='C', ln=True)
    pdf.cell(0, 8, 'mikkieworld.com', align='C', ln=True)

    # Quest pages
    for i, (title, desc) in enumerate(QUESTS):
        pdf.add_page()
        r, g, b = COLOR_LIST[i % len(COLOR_LIST)]

        # Header bar
        pdf.set_fill_color(r, g, b)
        pdf.rect(0, 0, 210, 40, 'F')

        pdf.set_font('Helvetica', 'B', 20)
        pdf.set_text_color(255, 255, 255)
        pdf.set_y(12)
        pdf.cell(0, 10, title, align='C', ln=True)

        # Mission number badge
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(r, g, b)
        pdf.set_line_width(2)

        # Description
        pdf.set_y(55)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 10, desc, align='C')

        # Drawing area
        pdf.ln(10)
        pdf.set_font('Helvetica', 'I', 11)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 8, 'Teken hier jouw avontuur:', align='C', ln=True)

        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.5)
        # Drawing box
        pdf.rect(20, pdf.get_y(), 170, 100)

        # Stars decoration
        pdf.set_y(pdf.get_y() + 110)
        pdf.set_font('Helvetica', '', 20)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 10, '* * * * * * *', align='C', ln=True)

        # Footer
        pdf.set_y(270)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 6, f'MIKKIE WORLD | mikkieworld.com | 7/7/2026 07:07 | Missie {i+1} van 7', align='C', ln=True)

    # Last page - CTA
    pdf.add_page()
    pdf.set_fill_color(59, 130, 246)
    pdf.rect(0, 0, 210, 297, 'F')

    pdf.set_y(60)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, 'Klaar voor meer?', align='C', ln=True)

    pdf.ln(10)
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(0, 12, 'Er zijn nog 70 missies te ontdekken!\nMet MIKKIE, BUBBLES, KNOEST,\nFIDO, NYX, ZERA en ORA.', align='C')

    pdf.ln(20)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 12, 'mikkieworld.com', align='C', ln=True)

    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'Launch: 7 juli 2026 om 07:07', align='C', ln=True)

    pdf.output(output_path)
    print(f"PDF aangemaakt: {output_path}")
    print(f"Paginas: {len(QUESTS) + 2}")
    print(f"Klaar om te uploaden naar Gumroad als gratis leadmagnet!")

output = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/MIKKIE_7_Missies.pdf')
create_pdf(output)
