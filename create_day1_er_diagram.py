from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas


OUTPUT = Path(__file__).parent / "day1_er_diagram.pdf"


TABLES = {
    "bm_customers": (40, 390),
    "bm_stores": (250, 390),
    "bm_skus": (460, 390),
    "bm_promotions": (670, 390),
    "bm_inventory": (250, 160),
    "bm_sales": (460, 130),
}


def draw_table(pdf, name, x, y):
    pdf.setFillColor(colors.HexColor("#17324D"))
    pdf.roundRect(x, y, 170, 58, 5, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x + 8, y + 39, name)
    pdf.setFont("Helvetica", 8)
    keys = {
        "bm_customers": "PK: cust_id",
        "bm_stores": "PK: store_id",
        "bm_skus": "PK: sku_id",
        "bm_promotions": "PK: promo_id",
        "bm_inventory": "PK/FK: store_id, sku_id",
        "bm_sales": "FK: store_id, sku_id, customer_id",
    }
    pdf.drawString(x + 8, y + 24, keys[name])


def connector(pdf, src, dst, label):
    x1, y1 = TABLES[src]
    x2, y2 = TABLES[dst]
    x1 += 85
    y1 += 8
    x2 += 85
    y2 += 58
    pdf.setStrokeColor(colors.HexColor("#C05621"))
    pdf.setLineWidth(1.2)
    pdf.line(x1, y1, x2, y2)
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    pdf.setFillColor(colors.HexColor("#7B341E"))
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(cx, cy + 4, label)


def main():
    pdf = canvas.Canvas(str(OUTPUT), pagesize=landscape(letter))
    pdf.setTitle("Day 1 ER Diagram")
    pdf.setFillColor(colors.HexColor("#102A43"))
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawString(40, 560, "Day 1 ER Diagram - retail_db")
    pdf.setFillColor(colors.HexColor("#486581"))
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, 545, "Source tables: bm_customers, bm_inventory, bm_promotions, bm_sales, bm_skus, bm_stores")

    for name, (x, y) in TABLES.items():
        draw_table(pdf, name, x, y)

    connector(pdf, "bm_customers", "bm_sales", "cust_id -> customer_id")
    connector(pdf, "bm_stores", "bm_sales", "store_id")
    connector(pdf, "bm_skus", "bm_sales", "sku_id")
    connector(pdf, "bm_stores", "bm_inventory", "store_id")
    connector(pdf, "bm_skus", "bm_inventory", "sku_id")

    pdf.setFillColor(colors.HexColor("#486581"))
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(670, 365, "No direct FK from promotions to sales")
    pdf.save()
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()