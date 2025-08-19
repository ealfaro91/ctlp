# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

from odoo import api, models, fields
import pytz


class DocumentSignature(models.AbstractModel):
    _name = 'document.signature.mixin'
    _description = 'Abstract Model for Document Signature'

    position = fields.Selection([
        ('top', 'Top'),
        ('footer', 'Footer'),],
        string='Posición de la firma',
        default='footer'
    )

    @staticmethod
    def attach_signature_to_pdf(pdf_binary_base64, signature_image_base64, quadrant=1):
        """Adjunta una firma en un cuadrante específico de la última página."""
        if not pdf_binary_base64 or not signature_image_base64:
            return pdf_binary_base64  # Si falta algo, no modificamos

        # Decodificar los datos binarios
        pdf_data = base64.b64decode(pdf_binary_base64)
        signature_image = base64.b64decode(signature_image_base64)

        # Leer el PDF original
        original_pdf = PdfReader(io.BytesIO(pdf_data))

        # Buscar última página válida
        last_page = None
        last_page_index = None
        for idx, page in reversed(list(enumerate(original_pdf.pages))):
            try:
                if hasattr(page, "mediabox") and len(page.mediabox) == 4:
                    last_page = page
                    last_page_index = idx
                    break
            except Exception:
                continue

        # Si no hay página válida, usar primera
        if last_page is None:
            last_page = original_pdf.pages[0]
            last_page_index = 0
            width, height = 595, 842  # tamaño A4 por defecto
        else:
            try:
                width = float(last_page.mediabox.width)
                height = float(last_page.mediabox.height)
            except Exception:
                width, height = 595, 842

        # Configurar posiciones de cuadrantes
        quadrant_positions = {
            1: (width - 150, height - 100),  # arriba derecha
            2: (50, height - 100),  # arriba izquierda
            3: (width - 150, 50),  # abajo derecha
            4: (50, 50),  # abajo izquierda
        }

        # Obtener coordenadas según el cuadrante
        x, y = quadrant_positions.get(quadrant, quadrant_positions[1])
        sig_width, sig_height = 120, 50

        # Crear PDF con la firma
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))
        can.setFillColor(colors.white)
        can.rect(x, y, sig_width, sig_height, fill=1, stroke=0)
        can.drawImage(ImageReader(io.BytesIO(signature_image)), x, y, width=sig_width, height=sig_height, mask='auto')
        can.save()

        # Fusionar firma con la última página
        packet.seek(0)
        signature_pdf = PdfReader(packet)
        writer = PdfWriter()

        for i, page in enumerate(original_pdf.pages):
            if i == last_page_index:
                page.merge_page(signature_pdf.pages[0])
            writer.add_page(page)

        # Guardar PDF final
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        return base64.b64encode(output_stream.read())
