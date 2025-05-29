"""Utils functions for the projects."""
from django.core.cache import cache

from io import BytesIO
import textwrap

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph

from django.utils.timezone import now


def generate_receipt(donation):
    """Generate a styled PDF receipt for a donation."""
    buffer = BytesIO()

    width, height = letter
    p = canvas.Canvas(buffer, pagesize=letter)

    receipt_number = f"REC-{donation.pk}-{now().strftime('%Y%m%d%H%M%S')}"

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=0.2 * inch)

    p.setFillColor(colors.darkblue)
    title = Paragraph('Donation Receipt', header_style)
    title.wrapOn(p, width - inch, height)
    title.drawOn(p, inch / 2, height - inch)

    p.setStrokeColor(colors.darkblue)
    p.line(inch / 2, height - 1.15 * inch, width - inch / 2, height - 1.15 * inch)
    p.line(inch / 2, height - 6.5 * inch, width - inch / 2, height - 6.5 * inch)

    p.setFillColor(colors.black)
    p.setFont('Helvetica-Bold', 12)
    p.drawString(inch / 2, height - 1.5 * inch, f'Receipt Number: {receipt_number}')
    p.drawString(inch / 2, height - 1.8 * inch, f"Date: {donation.created_at.strftime('%B %d, %Y at %I:%M %p')}")

    p.setFont('Helvetica-Bold', 12)
    p.drawString(inch / 2, height - 2.3 * inch, 'Donor Information:')
    p.setFont('Helvetica', 11)
    p.drawString(inch / 2, height - 2.6 * inch, f'Email: {donation.user.email}')
    name = f'{donation.user.first_name} {donation.user.last_name}'.strip()
    if name:
        p.drawString(inch / 2, height - 2.9 * inch, f'Name: {name}')

    p.setFont('Helvetica-Bold', 12)
    p.drawString(inch / 2, height - 3.4 * inch, 'Campaign Information:')
    p.setFont('Helvetica', 11)
    p.drawString(inch / 2, height - 3.7 * inch, f'Campaign: {donation.campaign.title}')

    description = donation.campaign.description
    if description:
        wrapped_text = textwrap.wrap(description, width=65)
        p.setFont('Helvetica', 9)
        y_position = height - 4.0 * inch
        for line in wrapped_text[:3]:
            p.drawString(inch / 2, y_position, line)
            y_position -= 0.2 * inch
        if len(wrapped_text) > 3:
            p.drawString(inch / 2, y_position, '...')

    p.setFont('Helvetica-Bold', 12)
    p.drawString(inch / 2, height - 5.0 * inch, 'Donation Details:')
    p.setFont('Helvetica', 11)
    p.drawString(inch / 2, height - 5.3 * inch, f'Amount: ${donation.amount:.2f}')
    p.drawString(inch / 2, height - 5.6 * inch, f"Date: {donation.created_at.strftime('%Y-%m-%d')}")
    p.drawString(inch / 2, height - 5.9 * inch, f"Time: {donation.created_at.strftime('%I:%M %p')}")

    p.setFont('Helvetica-Oblique', 10)
    thank_you = 'Thank you for your generous donation! Your contribution helps us make a difference.'
    p.drawString((width - p.stringWidth(thank_you, 'Helvetica-Oblique', 10)) / 2, height - 7.0 * inch, thank_you)

    p.setFont('Helvetica', 8)
    p.setFillColor(colors.gray)
    footer_text = 'This receipt is automatically generated and may be used for tax purposes.'
    p.drawString((width - p.stringWidth(footer_text, 'Helvetica', 8)) / 2, inch / 2, footer_text)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def invalidate_cache(*args):
    """Clear campaign-related cache."""
    for key in args:
        cache.delete(key)
