"""
build_metodichka_docx.py
========================
Генерирует docs/metodichka/Методичка.docx — короткую ознакомительную
методичку из трёх актов (формула → поверхность → лабиринт → A*).

План и структура: docs/metodichka/PLAN.md

Запуск:
    python3 scripts/build_metodichka_docx.py
"""

from __future__ import annotations

import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ────────────────────────────────────────────────────────────
# Пути
# ────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "docs", "metodichka", "Методичка.docx")
TITLE_IMAGE_PATH = os.path.join(PROJECT_ROOT, "assets", "metodichka", "title_image.png")
RENDERS_DIR = os.path.join(PROJECT_ROOT, "assets", "renders")


# ────────────────────────────────────────────────────────────
# Цвета (RGB)
# ────────────────────────────────────────────────────────────

COLOR_DARK      = RGBColor(0x1A, 0x1A, 0x2E)   # почти чёрный — заголовки
COLOR_ACCENT    = RGBColor(0x16, 0x21, 0x3E)   # тёмно-синий — H2
COLOR_BLUE      = RGBColor(0x0F, 0x3C, 0x78)   # синий — H3
COLOR_CODE_FG   = RGBColor(0x1E, 0x3A, 0x5F)   # тёмно-синий — текст кода


# ────────────────────────────────────────────────────────────
# Вспомогательные функции
# ────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color: str) -> None:
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_horizontal_rule(doc: Document) -> None:
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(4)
    para.paragraph_format.space_after = Pt(4)
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "C0C8D8")
    pBdr.append(bottom)
    pPr.append(pBdr)


# ────────────────────────────────────────────────────────────
# Стили параграфов
# ────────────────────────────────────────────────────────────

def h1(doc: Document, text: str) -> None:
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(24)
    para.paragraph_format.space_after = Pt(8)
    para.paragraph_format.keep_with_next = True
    run = para.add_run(text)
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = COLOR_DARK
    add_horizontal_rule(doc)


def h2(doc: Document, text: str) -> None:
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(16)
    para.paragraph_format.space_after = Pt(6)
    para.paragraph_format.keep_with_next = True
    run = para.add_run(text)
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = COLOR_ACCENT


def h3(doc: Document, text: str) -> None:
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(12)
    para.paragraph_format.space_after = Pt(4)
    para.paragraph_format.keep_with_next = True
    run = para.add_run(text)
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = COLOR_BLUE


def body(doc: Document, text: str, bold_parts: list[str] | None = None) -> None:
    """Обычный параграф. bold_parts — список подстрок для выделения жирным."""
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(3)
    para.paragraph_format.space_after = Pt(6)
    para.paragraph_format.first_line_indent = Cm(0.75)

    if not bold_parts:
        run = para.add_run(text)
        run.font.size = Pt(11)
    else:
        remaining = text
        for bp in bold_parts:
            idx = remaining.find(bp)
            if idx == -1:
                continue
            if idx > 0:
                r = para.add_run(remaining[:idx])
                r.font.size = Pt(11)
            r2 = para.add_run(bp)
            r2.bold = True
            r2.font.size = Pt(11)
            remaining = remaining[idx + len(bp):]
        if remaining:
            r = para.add_run(remaining)
            r.font.size = Pt(11)


def body_plain(doc: Document, text: str) -> None:
    """Параграф без отступа первой строки."""
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(3)
    para.paragraph_format.space_after = Pt(6)
    run = para.add_run(text)
    run.font.size = Pt(11)


def bullet(doc: Document, text: str) -> None:
    para = doc.add_paragraph(style="List Bullet")
    para.paragraph_format.left_indent = Cm(0.75)
    para.paragraph_format.space_before = Pt(2)
    para.paragraph_format.space_after = Pt(2)
    run = para.add_run(text)
    run.font.size = Pt(11)


def numbered(doc: Document, text: str) -> None:
    para = doc.add_paragraph(style="List Number")
    para.paragraph_format.left_indent = Cm(0.75)
    para.paragraph_format.space_before = Pt(2)
    para.paragraph_format.space_after = Pt(2)
    run = para.add_run(text)
    run.font.size = Pt(11)


def code_block(doc: Document, lines: list[str], caption: str = "") -> None:
    """Блок кода с моноширинным шрифтом и серым фоном."""
    if caption:
        cp = doc.add_paragraph()
        cp.paragraph_format.space_before = Pt(10)
        cp.paragraph_format.space_after = Pt(0)
        r = cp.add_run(f"  {caption}")
        r.italic = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x55, 0x66, 0x77)

    for line in lines:
        para = doc.add_paragraph()
        para.paragraph_format.space_before = Pt(0)
        para.paragraph_format.space_after = Pt(0)
        para.paragraph_format.left_indent = Cm(0.5)
        para.paragraph_format.right_indent = Cm(0.5)
        pPr = para._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "EEF2F8")
        pPr.append(shd)
        run = para.add_run(line if line else " ")
        run.font.name = "Courier New"
        run.font.size = Pt(9)
        run.font.color.rgb = COLOR_CODE_FG

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def shell_block(doc: Document, lines: list[str]) -> None:
    """Блок команд shell с зеленоватым фоном — отличается от Python-кода."""
    for line in lines:
        para = doc.add_paragraph()
        para.paragraph_format.space_before = Pt(0)
        para.paragraph_format.space_after = Pt(0)
        para.paragraph_format.left_indent = Cm(0.5)
        para.paragraph_format.right_indent = Cm(0.5)
        pPr = para._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "F0F7EC")
        pPr.append(shd)
        run = para.add_run(line if line else " ")
        run.font.name = "Courier New"
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x1F, 0x4A, 0x1F)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def note_box(doc: Document, text: str, prefix: str = "📌 Примечание") -> None:
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(8)
    para.paragraph_format.space_after = Pt(8)
    para.paragraph_format.left_indent = Cm(0.5)
    para.paragraph_format.right_indent = Cm(0.5)
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "FFF8DC")
    pPr.append(shd)
    r1 = para.add_run(f"{prefix}:  ")
    r1.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = RGBColor(0x7A, 0x5C, 0x00)
    r2 = para.add_run(text)
    r2.font.size = Pt(10)
    r2.font.color.rgb = RGBColor(0x4A, 0x3C, 0x00)


def screenshot_placeholder(doc: Document, rel_path: str, caption: str) -> None:
    """Вставляет место для скриншота: рамка с подсказкой о том, какую картинку
    сюда нужно вручную добавить. Картинка не встраивается — пользователь
    вставит её сам в DOCX-редакторе.
    """
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before = Pt(12)
    para.paragraph_format.space_after = Pt(2)
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "E8F4FF")
    pPr.append(shd)

    r1 = para.add_run("📸  МЕСТО ДЛЯ КАРТИНКИ\n")
    r1.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    r2 = para.add_run(f"Вставить файл: {rel_path}\n")
    r2.font.size = Pt(9)
    r2.font.color.rgb = RGBColor(0x1A, 0x5C, 0xAA)

    r3 = para.add_run(caption)
    r3.italic = True
    r3.font.size = Pt(9)
    r3.font.color.rgb = RGBColor(0x55, 0x66, 0x88)

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(10)


# ────────────────────────────────────────────────────────────
# Настройка страницы
# ────────────────────────────────────────────────────────────

def setup_page(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width  = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.0)
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)

    # Нумерация страниц в нижнем колонтитуле
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_para.clear()
    run = footer_para.add_run("Страница ")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x99)
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run2 = footer_para.add_run()
    run2.font.size = Pt(9)
    run2._r.append(fldChar1)
    run2._r.append(instrText)
    run2._r.append(fldChar2)

    # Колонтитул сверху
    header = section.header
    header_para = header.paragraphs[0]
    header_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = header_para.add_run("Математика в 3D: от формулы к маршруту")
    r.font.size = Pt(8)
    r.italic = True
    r.font.color.rgb = RGBColor(0x88, 0x88, 0x99)


# ────────────────────────────────────────────────────────────
# Титульная страница
# ────────────────────────────────────────────────────────────

def build_title_page(doc: Document) -> None:
    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = t.add_run("STEM-ПРОЕКТ")
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x55, 0x66, 0x88)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    t2 = doc.add_paragraph()
    t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = t2.add_run("Математика в 3D:\nот формулы к маршруту")
    run2.bold = True
    run2.font.size = Pt(24)
    run2.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("Ознакомительная методичка по Blender + Python")
    r.italic = True
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor(0x44, 0x55, 0x77)

    add_horizontal_rule(doc)
    doc.add_paragraph().paragraph_format.space_after = Pt(20)

    for line in [
        "Предмет: математика + информатика + 3D-технологии",
        "Класс: 10–11 / первый курс",
        "Инструменты: Blender 4.x/5.x, Python 3.10+",
        "Ориентировочное время: 2–3 учебных часа",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(line)
        r.font.size = Pt(12)

    # Титульная иллюстрация — скриншот Blender со сценой FunctionVisualizer
    if os.path.exists(TITLE_IMAGE_PATH):
        img_para = doc.add_paragraph()
        img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_para.paragraph_format.space_before = Pt(18)
        img_para.paragraph_format.space_after = Pt(6)
        run_img = img_para.add_run()
        run_img.add_picture(TITLE_IMAGE_PATH, width=Cm(15.0))

        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = cap.add_run("Blender со сценой FunctionVisualizer — волновая поверхность в 3D Viewport")
        cr.italic = True
        cr.font.size = Pt(9)
        cr.font.color.rgb = RGBColor(0x55, 0x66, 0x88)

    doc.add_page_break()


# ────────────────────────────────────────────────────────────
# Введение
# ────────────────────────────────────────────────────────────

def build_intro(doc: Document) -> None:
    h1(doc, "Введение")

    body(doc,
        "Математика в учебнике — это символы на бумаге. Увидеть, как на самом "
        "деле выглядит формула z = sin(x) · cos(y), без 3D-инструмента почти "
        "невозможно. А потом ещё объяснить, как компьютер находит путь в "
        "лабиринте.",
        bold_parts=["z = sin(x) · cos(y)"])
    body(doc,
        "Эта методичка — короткая экскурсия по трём маленьким идеям:")

    numbered(doc,
        "Формула становится формой. Любая функция двух переменных — это "
        "поверхность в пространстве. Мы зададим её одной строчкой Python и "
        "увидим 3D-модель.")
    numbered(doc,
        "Лабиринт как мир из кубиков. Любую сетку из нулей и единиц можно "
        "превратить в Blender-сцену. Каждая «единица» — один куб.")
    numbered(doc,
        "Компьютер ищет выход. Алгоритм A* (произносится «эй-стар») находит "
        "кратчайший путь в лабиринте за доли секунды. Мы увидим, как он это "
        "делает — и увидим сам маршрут в 3D.")

    h2(doc, "Как читать")
    body(doc,
        "Три акта, три картинки, три команды для запуска. В каждом акте "
        "есть короткое объяснение «простыми словами», минимальный сниппет "
        "кода и одна CLI-команда, которую можно скопировать и запустить. "
        "Полные листинги скриптов в методичку не включены — они лежат в "
        "папке scripts/ репозитория. Так методичка остаётся короткой, а "
        "код — всегда актуальным.",
        bold_parts=["scripts/"])

    h2(doc, "Что нужно установить")
    bullet(doc, "Blender 4.5 или новее (blender.org, бесплатно).")
    bullet(doc, "Python 3.10+ идёт в комплекте с Blender — отдельно ставить не нужно.")
    bullet(doc, "Git для клонирования репозитория (необязательно — можно скачать ZIP).")

    h2(doc, "Как получить проект и запустить первый пример")
    shell_block(doc, [
        "git clone <репозиторий>",
        "cd stem-blender-math-visualization",
        "blender --background --python scripts/visualize_function.py -- \\",
        "    --function wave --output assets/renders/wave_A1_k1.png",
    ])
    body(doc,
        "После запуска в папке assets/renders/ появится картинка волновой "
        "поверхности. Если она появилась — всё настроено правильно, можно "
        "переходить к Акту 1.",
        bold_parts=["assets/renders/"])

    note_box(doc,
        "Флаг --background запускает Blender без графического интерфейса, а "
        "аргументы после -- передаются в наш Python-скрипт. Это стандартный "
        "способ автоматизировать Blender из командной строки.")

    doc.add_page_break()


# ────────────────────────────────────────────────────────────
# Акт 1. Формула становится формой
# ────────────────────────────────────────────────────────────

def build_act1(doc: Document) -> None:
    h1(doc, "Акт 1. Формула становится формой")

    screenshot_placeholder(doc,
                "assets/renders/wave_A1_k1.png",
                "Поверхность z = sin(x) · cos(y) в 3D. Цвет — по высоте: "
                "синий внизу, красный наверху.")

    h2(doc, "1.1 Что мы видим")
    body(doc,
        "На картинке — мягкая рябь, как на поверхности воды. Впадины и "
        "горки чередуются по диагоналям. Это одна формула. Без компьютера "
        "её так не увидеть — можно только вообразить по графикам сечений.",
        bold_parts=["мягкая рябь"])

    h2(doc, "1.2 Как это работает")
    body(doc,
        "Функция двух переменных z = f(x, y) задаёт поверхность: для "
        "каждой точки (x, y) на плоскости есть своя высота z.",
        bold_parts=["z = f(x, y)"])
    body_plain(doc, "Алгоритм построения:")
    numbered(doc,
        "Берём сетку точек на плоскости. Например, 100×100 точек в "
        "квадрате от −5 до 5 по обеим осям.")
    numbered(doc,
        "Для каждой точки считаем z = f(x, y) — получаем тройку (x, y, z).")
    numbered(doc,
        "Отдаём все тройки Blender'у. Blender соединяет соседние точки "
        "четырёхугольниками — получается поверхность.")
    numbered(doc,
        "Красим поверхность по высоте: чем выше z, тем краснее; чем ниже — "
        "тем синее.")

    h2(doc, "1.3 Ключевой код")
    code_block(doc, [
        "import math",
        "",
        "def wave(x, y):",
        "    return math.sin(x) * math.cos(y)",
        "",
        "# сетка 100x100 в квадрате [-5, 5]",
        "vertices = []",
        "for i in range(100):",
        "    for j in range(100):",
        "        x = -5 + i * 0.1",
        "        y = -5 + j * 0.1",
        "        z = wave(x, y)",
        "        vertices.append((x, y, z))",
    ])
    body(doc,
        "Всё остальное — создание mesh'а, настройка камеры, покраска — "
        "лежит в scripts/visualize_function.py и scripts/function_library.py. "
        "Посмотри туда, если интересно, как это устроено.",
        bold_parts=["scripts/visualize_function.py", "scripts/function_library.py"])

    h2(doc, "1.4 Запуск")
    shell_block(doc, [
        "blender --background --python scripts/visualize_function.py -- \\",
        "    --function wave --output assets/renders/wave_A1_k1.png",
    ])
    body(doc,
        "Замени wave на paraboloid, saddle, ripple или gaussian — получишь "
        "другие поверхности. Все готовые рендеры для сравнения лежат в "
        "assets/renders/.",
        bold_parts=["wave", "paraboloid", "saddle", "ripple", "gaussian"])

    h2(doc, "1.5 Задание для ученика")
    bullet(doc,
        "Открой scripts/function_library.py и найди там функцию wave. "
        "Измени коэффициент частоты и перегенерируй картинку. Как изменился "
        "рельеф?")
    bullet(doc,
        "Придумай свою функцию — например, z = x² − y². Что получится?")

    doc.add_page_break()


# ────────────────────────────────────────────────────────────
# Акт 2. Лабиринт как мир из кубиков
# ────────────────────────────────────────────────────────────

def build_act2(doc: Document) -> None:
    h1(doc, "Акт 2. Лабиринт как мир из кубиков")

    screenshot_placeholder(doc,
                "assets/renders/labyrinth_cubes.png",
                "Лабиринт 15×15, сгенерированный случайно. "
                "Каждая стена — один куб в Blender-сцене.")

    h2(doc, "2.1 Что мы видим")
    body(doc,
        "Настоящий 3D-лабиринт. Но внутри программы он выглядит просто — "
        "таблица нулей и единиц. Ноль = пол (можно ходить), единица = "
        "стена (нельзя). Blender берёт эту таблицу и для каждой единицы "
        "ставит куб.",
        bold_parts=["таблица нулей и единиц"])

    h2(doc, "2.2 Как это работает")
    numbered(doc,
        "Сетка данных. Берём матрицу размера N×N из нулей и единиц.")
    numbered(doc,
        "Генерация лабиринта. Используем алгоритм рекурсивного бэктрекинга: "
        "ставим «копателя» в клетку, прорубаем коридоры в случайных "
        "направлениях, откатываемся, когда упёрлись в тупик. В итоге "
        "получается связный лабиринт без изолированных комнат.")
    numbered(doc,
        "Отрисовка. Для каждой клетки-единицы вызываем "
        "bpy.ops.mesh.primitive_cube_add(location=(x, y, 0.5)). Всё. Пол — "
        "один большой плоский прямоугольник под всем лабиринтом.")

    h2(doc, "2.3 Ключевой код")
    code_block(doc, [
        "import bpy",
        "",
        "maze = [  # 1 = стена, 0 = пол",
        "    [1,1,1,1,1],",
        "    [1,0,0,0,1],",
        "    [1,0,1,0,1],",
        "    [1,0,0,0,1],",
        "    [1,1,1,1,1],",
        "]",
        "for y, row in enumerate(maze):",
        "    for x, cell in enumerate(row):",
        "        if cell == 1:",
        "            bpy.ops.mesh.primitive_cube_add(location=(x, y, 0.5))",
    ])
    body(doc,
        "В реальном скрипте (scripts/pathfinding/visualize_labyrinth_in_blender.py) "
        "стены сделаны одним большим mesh'ом, а не десятками отдельных "
        "кубов — это быстрее при рендере. Но идея та же самая: «единица → куб».",
        bold_parts=["scripts/pathfinding/visualize_labyrinth_in_blender.py"])

    h2(doc, "2.4 Запуск")
    shell_block(doc, [
        "blender --background \\",
        "  --python scripts/pathfinding/visualize_labyrinth_in_blender.py -- \\",
        "    --rows 15 --cols 15 --seed 7 --no-path \\",
        "    --output assets/renders/labyrinth_cubes.png",
    ])
    body(doc,
        "Меняй --seed — получишь каждый раз новый лабиринт. Меняй --rows и "
        "--cols (нечётные числа) — изменишь размер.",
        bold_parts=["--seed", "--rows", "--cols"])

    h2(doc, "2.5 Задание для ученика")
    body(doc,
        "Запусти скрипт с размером 25×25 и --seed 1, потом 25×25 и --seed 2. "
        "Сравни лабиринты. Почему они разные, если код один и тот же? Что "
        "такое seed и зачем он нужен?",
        bold_parts=["seed"])

    doc.add_page_break()


# ────────────────────────────────────────────────────────────
# Акт 3. Компьютер ищет выход
# ────────────────────────────────────────────────────────────

def build_act3(doc: Document) -> None:
    h1(doc, "Акт 3. Компьютер ищет выход")

    screenshot_placeholder(doc,
                "assets/renders/labyrinth_solved.png",
                "Тот же лабиринт. Алгоритм A* за долю секунды нашёл "
                "кратчайший путь от зелёной точки к жёлтой. "
                "Маршрут — розовая линия.")

    h2(doc, "3.1 Что мы видим")
    body(doc,
        "Компьютер не «смотрит» на лабиринт глазами. Ему нужно правило, по "
        "которому решать: в какую клетку идти дальше? Правил много. Самое "
        "популярное для поиска пути — алгоритм A* (А-звёздочка).",
        bold_parts=["правило", "A*"])

    h2(doc, "3.2 Как работает A* (простыми словами)")
    body(doc,
        "Представь, что ты стоишь на старте и держишь в голове список "
        "«клеток на рассмотрение».")
    numbered(doc, "Смотришь на соседей текущей клетки.")
    numbered(doc,
        "Для каждого соседа считаешь две цифры: "
        "g — сколько шагов уже прошёл от старта до этой клетки; "
        "h — сколько шагов по прямой осталось до финиша (эвристика — "
        "приблизительная оценка остатка пути).")
    numbered(doc,
        "Складываешь: f = g + h. Это оценка, «насколько перспективна» клетка.")
    numbered(doc, "Идёшь в клетку с наименьшим f.")
    numbered(doc, "Повторяешь, пока не придёшь в финиш.")
    numbered(doc,
        "По дороге запоминаешь: «в клетку X я пришёл из клетки Y». В конце "
        "разматываешь эту цепочку назад — получаешь сам маршрут.")

    note_box(doc,
        "Эвристика h не даёт алгоритму «блуждать» в противоположную от "
        "финиша сторону. Без h (это уже алгоритм Dijkstra) компьютер "
        "проверяет гораздо больше клеток, но всё равно находит ответ.")

    h2(doc, "3.3 Ключевой код")
    code_block(doc, [
        "import heapq",
        "",
        "open_set = [(0, start)]            # (оценка f, клетка)",
        "g_score = {start: 0}",
        "came_from = {start: None}",
        "",
        "while open_set:",
        "    _, current = heapq.heappop(open_set)",
        "    if current == goal:",
        "        break",
        "    for neighbor in neighbors(current):",
        "        tentative_g = g_score[current] + 1",
        "        if tentative_g < g_score.get(neighbor, float('inf')):",
        "            g_score[neighbor] = tentative_g",
        "            f = tentative_g + heuristic(neighbor, goal)",
        "            heapq.heappush(open_set, (f, neighbor))",
        "            came_from[neighbor] = current",
    ])
    body(doc,
        "Это сердце A*. Весь боевой код (с препятствиями, разными "
        "алгоритмами и весами рёбер) — в scripts/pathfinding/search.py и "
        "scripts/pathfinding/cost_functions.py.",
        bold_parts=["scripts/pathfinding/search.py",
                    "scripts/pathfinding/cost_functions.py"])

    h2(doc, "3.4 Запуск")
    shell_block(doc, [
        "blender --background \\",
        "  --python scripts/pathfinding/visualize_labyrinth_in_blender.py -- \\",
        "    --rows 15 --cols 15 --seed 7 --algorithm astar \\",
        "    --output assets/renders/labyrinth_solved.png",
    ])
    body(doc,
        "Поменяй --algorithm astar на --algorithm dijkstra. Маршрут "
        "получится таким же (или почти таким же по длине), но в логе "
        "«посещено=...» Dijkstra проверит больше клеток, потому что у "
        "него нет эвристики.",
        bold_parts=["--algorithm astar", "--algorithm dijkstra"])

    h2(doc, "3.5 Задание для ученика")
    bullet(doc,
        "Запусти A* и Dijkstra на одном и том же лабиринте (один --seed). "
        "Сравни значения «посещено узлов» в логе. Во сколько раз A* "
        "эффективнее?")
    bullet(doc,
        "Придумай свою эвристику. Что будет, если h = 0 всегда? А если h "
        "в 10 раз больше реального расстояния до финиша?")

    doc.add_page_break()


# ────────────────────────────────────────────────────────────
# Заключение
# ────────────────────────────────────────────────────────────

def build_conclusion(doc: Document) -> None:
    h1(doc, "Заключение")

    body(doc,
        "Три картинки — три разных мира внутри одной 3D-сцены:")
    bullet(doc, "поверхность — мир, заданный формулой;")
    bullet(doc, "лабиринт — мир, заданный таблицей;")
    bullet(doc, "маршрут — мир, заданный алгоритмом.")

    body(doc,
        "Во всех трёх случаях математика и программирование работают "
        "вместе: Python считает, Blender показывает. Это и есть основа "
        "вычислительной геометрии, компьютерной графики и игр — от "
        "школьного уровня до игровых студий.")

    h2(doc, "Куда двигаться дальше")
    bullet(doc,
        "Поверхность с препятствиями. Можно искать путь не только в "
        "плоском лабиринте, но и по «горам» — см. "
        "scripts/pathfinding/visualize_path_in_blender.py и рендеры "
        "assets/renders/path_*.png.")
    bullet(doc,
        "Geometry Nodes: интерактивный эквивалент того же, что мы делали "
        "кодом, только мышкой в Blender'е. См. "
        "scripts/setup_geometry_nodes_surface.py.")
    bullet(doc,
        "Более подробная методичка с разбором каждого файла проекта "
        "лежит в docs/metodichka/old/методичка_подробная.md — она для "
        "тех, кому интересна «внутрянка».")

    note_box(doc,
        "Полный код всех скриптов — в папке scripts/ репозитория. "
        "Методичка специально оставлена короткой: она вводит в тему, "
        "а код — в файлах, которые можно открыть, запустить и изменить.",
        prefix="Где взять код")


# ────────────────────────────────────────────────────────────
# Основная функция
# ────────────────────────────────────────────────────────────

def build_docx() -> None:
    print("[START] Создание Методичка.docx ...")

    doc = Document()
    setup_page(doc)

    # Базовый стиль
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.paragraph_format.line_spacing = Pt(14)

    build_title_page(doc)
    build_intro(doc)
    build_act1(doc)
    build_act2(doc)
    build_act3(doc)
    build_conclusion(doc)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    doc.save(OUTPUT_PATH)
    size_kb = os.path.getsize(OUTPUT_PATH) // 1024
    print(f"[DONE] Сохранено: {OUTPUT_PATH}  ({size_kb} KB)")


if __name__ == "__main__":
    build_docx()
