# -*- coding: utf-8 -*-

import base64
import io

import datetime

from dateutil.relativedelta import relativedelta

import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfFileReader, PdfFileWriter  # 👈 API vieja


# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.utils import ImageReader
# from reportlab.lib import colors

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
    def attach_signature_to_pdf(pdf_binary_base64, signature_image_base64, quadrant=3):
        """Adjunta una firma en un cuadrante específico de la última página."""

        if not pdf_binary_base64 or not signature_image_base64:
            return pdf_binary_base64  # Si falta algo, no modificamos

            # Decodificar los datos binarios
        pdf_data = base64.b64decode(pdf_binary_base64)
        signature_image = base64.b64decode(signature_image_base64)

        # Leer el PDF original
        original_pdf = PdfFileReader(io.BytesIO(pdf_data))

        # Buscar última página válida
        last_page = None
        last_page_index = None
        for idx in reversed(range(original_pdf.numPages)):
            page = original_pdf.getPage(idx)
            try:
                if hasattr(page, "mediaBox") and len(page.mediaBox) == 4:
                    last_page = page
                    last_page_index = idx
                    break
            except Exception:
                continue

        # Si no hay página válida, usar primera
        if last_page is None:
            last_page = original_pdf.getPage(0)
            last_page_index = 0
            width, height = 595, 842  # tamaño A4 por defecto
        else:
            try:
                width = float(last_page.mediaBox.getWidth())
                height = float(last_page.mediaBox.getHeight())
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
        x, y = quadrant_positions.get(quadrant, quadrant_positions[4])
        sig_width, sig_height = 120, 50

        # Crear PDF con la nueva firma
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))

        # Dibujar la firma (sin borrar lo anterior)
        can.drawImage(ImageReader(io.BytesIO(signature_image)), x, y,
                      width=sig_width, height=sig_height, mask='auto')

        # Agregar texto debajo de la firma
        text_x = x
        text_y = y - 12  # 12 puntos debajo de la firma
        can.setFont("Helvetica", 10)
        can.setFillColor(colors.black)
        can.drawString(text_x, text_y, f"Aprobado por:")

        can.save()

        # Fusionar firma con la última página
        packet.seek(0)
        signature_pdf = PdfFileReader(packet)
        writer = PdfFileWriter()

        for i in range(original_pdf.numPages):
            page = original_pdf.getPage(i)
            if i == last_page_index:
                page.mergePage(signature_pdf.getPage(0))  # API vieja
            writer.addPage(page)

        # Guardar PDF final
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        return base64.b64encode(output_stream.read())
