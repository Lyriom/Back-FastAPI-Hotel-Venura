from __future__ import annotations

from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle
from reportlab.lib import colors


def _build_doc(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Hotel Ventura",
    )


def generate_welcome_pdf(out_path: Path, hotel_name: str = "Hotel Ventura") -> Path:
    """
    PDF estático: Bienvenida + reglas generales (ajustables).
    """
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], spaceAfter=12)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], spaceBefore=10, spaceAfter=8)
    body = styles["BodyText"]

    rules = [
        "Check-in desde 14:00 y check-out hasta 12:00 (ajusta horarios según tu hotel).",
        "Presentar documento de identidad al ingresar.",
        "Prohibido fumar en habitaciones y áreas internas.",
        "Evitar ruidos fuertes entre 22:00 y 08:00.",
        "Cuidar instalaciones; daños intencionales podrán ser cobrados.",
        "No se permite el ingreso de personas no registradas sin autorización de recepción.",
        "Política de mascotas: (define aquí si tu hotel permite o no).",
    ]

    doc = _build_doc(out_path)
    story = [
        Paragraph(f"¡Bienvenido a {hotel_name}!", h1),
        Paragraph("Gracias por elegirnos. A continuación encontrarás reglas generales y recomendaciones para tu estadía.", body),
        Spacer(1, 10),
        Paragraph("Reglas y recomendaciones", h2),
        ListFlowable(
            [ListItem(Paragraph(r, body), leftIndent=14) for r in rules],
            bulletType="bullet",
            leftIndent=18,
        ),
        Spacer(1, 12),
        Paragraph(
            f"Documento generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            ParagraphStyle("small", parent=body, fontSize=9, textColor=colors.grey),
        ),
    ]
    doc.build(story)
    return out_path


def generate_reservation_pdf(
    out_path: Path,
    *,
    hotel_name: str,
    reservation_id: int,
    guest_fullname: str,
    guest_email: str,
    room_numero: str,
    room_tipo: str,
    fecha_inicio: str,
    fecha_fin: str,
    costo_total: str,
    status: str,
) -> Path:
    """
    PDF de reserva: comprobante + resumen + reglas (puedes reusar el texto estilo “Gracias por su reserva”).
    """
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], spaceAfter=12)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], spaceBefore=10, spaceAfter=8)
    body = styles["BodyText"]

    doc = _build_doc(out_path)

    table_data = [
        ["Reserva #", str(reservation_id)],
        ["Huésped", guest_fullname],
        ["Email", guest_email],
        ["Habitación", f"{room_numero} ({room_tipo})"],
        ["Fechas", f"{fecha_inicio} → {fecha_fin}"],
        ["Total", f"${costo_total}"],
        ["Estado", status],
    ]

    tbl = Table(table_data, colWidths=[110, 360])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    # Puedes inspirarte en el formato “¡Gracias por su Reserva!” del PDF de ejemplo (estructura por secciones),
    # cambiando el contenido a tu hotel. :contentReference[oaicite:2]{index=2}
    story = [
        Paragraph(f"{hotel_name} — Confirmación de Reserva", h1),
        Paragraph("¡Gracias por su reserva! Este documento sirve como comprobante informativo.", body),
        Spacer(1, 10),
        tbl,
        Spacer(1, 14),
        Paragraph("Reglas rápidas", h2),
        ListFlowable(
            [
                ListItem(Paragraph("Check-in/Check-out según política del hotel.", body), leftIndent=14),
                ListItem(Paragraph("Presentar identificación al ingreso.", body), leftIndent=14),
                ListItem(Paragraph("Política de mascotas: define si aplica (en el ejemplo se especifica que no se permiten).", body), leftIndent=14),
            ],
            bulletType="bullet",
            leftIndent=18,
        ),
        Spacer(1, 12),
        Paragraph(
            f"Documento generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            ParagraphStyle("small", parent=body, fontSize=9, textColor=colors.grey),
        ),
    ]
    doc.build(story)
    return out_path
