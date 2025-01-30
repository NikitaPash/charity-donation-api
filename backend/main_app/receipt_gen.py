from io import BytesIO

from reportlab.pdfgen import canvas

from django.utils.timezone import now


def generate_receipt(donation):
    """Generate a PDF receipt for a donation."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    receipt_number = f"REC-{donation.pk}-{now().strftime('%Y%m%d%H%M%S')}"

    p.drawString(100, 750, 'Donation Receipt')
    p.drawString(100, 730, f'Receipt Number: {receipt_number}')
    p.drawString(100, 710, f"Date: {donation.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, 690, f'Donor: {donation.user.email}')
    p.drawString(100, 670, f'Campaign: {donation.campaign.title}')
    p.drawString(100, 650, f'Amount: ${donation.amount}')

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
