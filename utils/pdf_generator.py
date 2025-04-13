from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
import base64
from fpdf import FPDF

def generate_pdf_invoice(db_manager_instance, invoice_id):
    """
    Generates a PDF invoice using ReportLab.

    Args:
        db_manager_instance: Database manager instance for executing queries.
        invoice_id: ID of the invoice to generate.

    Returns:
        PDF data as bytes or None if invoice not found.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Fetch invoice header information
    invoice_query = "SELECT i.id, i.invoice_date, i.total_amount, s.status_name, " \
                    "c.first_name AS customer_first_name, c.last_name AS customer_last_name, " \
                    "c.email AS customer_email, c.phone AS customer_phone " \
                    "FROM invoices i " \
                    "JOIN statuses s ON i.status_id = s.id " \
                    "JOIN users c ON i.customer_id = c.id " \
                    "WHERE i.id = %s"
    invoice_data = db_manager_instance.execute_query(invoice_query, (invoice_id,), fetch='one')

    if not invoice_data:
        return None

    inv_id, inv_date, total_amount, status, cust_fname, cust_lname, cust_email, cust_phone = invoice_data

    story.append(Paragraph(f"<b>Invoice ID:</b> {inv_id}", styles['h2']))
    story.append(Paragraph(f"<b>Date:</b> {inv_date.strftime('%Y-%m-%d')}", styles['h4']))
    story.append(Paragraph(f"<b>Status:</b> {status}", styles['h4']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Customer Information:</b>", styles['h3']))
    story.append(Paragraph(f"{cust_fname} {cust_lname}", styles['normal']))
    story.append(Paragraph(cust_email, styles['normal']))
    story.append(Paragraph(cust_phone, styles['normal']))
    story.append(Spacer(1, 12))

    # Fetch invoice items
    items_query = "SELECT ii.quantity, ii.total_price, it.description, it.price " \
                   "FROM invoice_items ii " \
                   "JOIN items it ON ii.item_id = it.id " \
                   "WHERE ii.invoice_id = %s"
    items_data = db_manager_instance.execute_query(items_query, (invoice_id,), fetch='all')

    if items_data:
        data = [["Quantity", "Description", "Unit Price", "Total Price"]]
        for qty, total_price, desc, unit_price in items_data:
            data.append([qty, desc, f"${unit_price:.2f}", f"${total_price:.2f}"])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Total Amount:</b> ${total_amount:.2f}", styles['h3']))
    else:
        story.append(Paragraph("No items found for this invoice.", styles['normal']))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_invoice_pdf(invoice_details, invoice_items, file_path):
    """Generates a PDF for an invoice with details and items."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Invoice #{invoice_details[0]}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Customer ID: {invoice_details[1]}", ln=True)
    pdf.cell(200, 10, txt=f"Invoice Date: {invoice_details[2]}", ln=True)
    pdf.cell(200, 10, txt=f"Total Amount: {invoice_details[3]}", ln=True)
    pdf.cell(200, 10, txt=f"Status: {invoice_details[4]}", ln=True)
    pdf.ln(10)

    pdf.cell(200, 10, txt="Items:", ln=True)
    pdf.cell(30, 10, txt="Item ID", border=1)
    pdf.cell(60, 10, txt="Description", border=1)
    pdf.cell(30, 10, txt="Vendor", border=1)
    pdf.cell(20, 10, txt="Quantity", border=1)
    pdf.cell(30, 10, txt="Unit Price", border=1)
    pdf.cell(30, 10, txt="Total Price", border=1)
    pdf.ln()
    for item_id, description, vendor_name, quantity, unit_price, total_price in invoice_items:
        pdf.cell(30, 10, txt=str(item_id), border=1)
        pdf.cell(60, 10, txt=description, border=1)
        pdf.cell(30, 10, txt=vendor_name, border=1)
        pdf.cell(20, 10, txt=str(quantity), border=1)
        pdf.cell(30, 10, txt=f"${unit_price:.2f}", border=1)
        pdf.cell(30, 10, txt=f"${total_price:.2f}", border=1)
        pdf.ln()

    pdf.output(file_path)
