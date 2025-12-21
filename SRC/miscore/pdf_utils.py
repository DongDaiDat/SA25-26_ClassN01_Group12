# miscore/pdf_utils.py
from io import BytesIO
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def ensure_unicode_font():
    """Đăng ký font Unicode (DejaVu) nếu có, fallback Helvetica."""
    try:
        pdfmetrics.getFont("DejaVu")
    except Exception:
        try:
            pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
        except Exception:
            pass

def render_curriculum_pdf(curriculum, items, total_active_credits: Decimal):
    """
    Trả về bytes PDF danh sách học phần cho 1 CTĐT.
    - curriculum: obj Curriculum (đã select_related major, faculty)
    - items: queryset/iter ListCourse (đã select_related course), order theo (semester_no, course__code)
    - total_active_credits: Decimal
    """
    ensure_unicode_font()
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # chọn font
    try:
        p.setFont("DejaVu", 12)
        font = "DejaVu"
    except Exception:
        p.setFont("Helvetica", 12)
        font = "Helvetica"

    def header():
        p.setFont(font, 14)
        p.drawString(2*cm, height - 2.2*cm, "DANH SÁCH HỌC PHẦN CHƯƠNG TRÌNH ĐÀO TẠO")
        p.setFont(font, 11)
        p.drawString(2*cm, height - 3.0*cm, f"Ngành: {curriculum.major}")
        p.drawString(2*cm, height - 3.6*cm, f"Khoa: {curriculum.faculty}    Năm: {curriculum.year}")
        p.line(2*cm, height - 3.9*cm, width - 2*cm, height - 3.9*cm)

    def table_header(y):
        p.setFont(font, 10)
        p.drawString(2*cm,  y, "Mã HP")
        p.drawString(5*cm,  y, "Tên học phần")
        p.drawString(13.5*cm, y, "TC")
        p.drawString(15.2*cm, y, "LT")
        p.drawString(16.6*cm, y, "TH")
        p.drawString(18.0*cm, y, "Kỳ")
        p.drawString(19.5*cm, y, "Loại")
        return y - 0.5*cm

    def maybe_new_page(y):
        if y < 2.5*cm:
            p.showPage()
            p.setFont(font, 12)
            header()
            y = table_header(height - 5*cm)
        return y

    y = height - 5*cm
    header()
    y = table_header(y)

    current_sem = None
    for it in items:
        c = it.course
        if it.semester_no != current_sem:
            y = maybe_new_page(y)
            p.setFont(font, 10)
            p.drawString(2*cm, y, f"— Kỳ {it.semester_no}")
            y -= 0.4*cm
            current_sem = it.semester_no

        y = maybe_new_page(y)
        p.setFont(font, 10)
        p.drawString(2*cm, y, c.code or "")
        p.drawString(5*cm, y, (c.name or "")[:60])
        p.drawRightString(14.8*cm, y, f"{(c.credits or 0):.1f}")
        p.drawRightString(16.2*cm, y, f"{(c.credits_lt or 0):.1f}")
        p.drawRightString(17.6*cm, y, f"{(c.credits_th or 0):.1f}")
        p.drawRightString(19.2*cm, y, f"{it.semester_no}")
        p.drawString(19.6*cm, y, "BB" if it.requirement_type == "COMPULSORY" else "TC")
        y -= 0.36*cm

    y = maybe_new_page(y)
    p.setFont(font, 11)
    p.line(2*cm, y, width - 2*cm, y)
    y -= 0.5*cm
    p.drawString(2*cm, y, f"TỔNG SỐ TÍN CHỈ (Active): {float(total_active_credits):.1f}")

    p.showPage()
    p.save()
    pdf = buf.getvalue()
    buf.close()
    return pdf
