
from odoo import api, fields , models

import base64
import datetime
import io
import pytz

from dateutil.relativedelta import relativedelta

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfFileReader, PdfFileWriter  # 👈 API vieja


class ApprovalLog(models.Model):
    _name = "approval.log"
    _description = "Approval log"
    _order = "id desc"

    sequence = fields.Integer(
        string="Sequence",
        required=False,
        tracking=True
    )
    role_id = fields.Many2one(
        "res.groups",
        string="Role",
        tracking=True
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        tracking=True,
        domain="[('share', '=', False)]"
    #    domain="[('id', 'in', user_ids)]",
    )
    user_ids = fields.Many2many(
        "res.users",
        string="Users",
        compute="_compute_user_ids",
    )
    image = fields.Binary(
        string="Image",
        related="user_id.image_1920",
        readonly=True,
        help="Image of the user who made the approval."
    )
    state = fields.Selection([
        ("pending", "Pending"),
        ("approved", "Approved")],
        string="Status",
        default="pending",
        tracking=True
    )
    approval_type = fields.Selection(
        [("author", "Author"),
         ("reviewer", "Reviewer"),
         ("approver", "Approver")],
        string="Approval Type",
        default="approver",
        tracking=True
    )
    request_sign_date = fields.Datetime(
        string="Request sign date",
        tracking=True
    )
    signed_date = fields.Datetime(
        string="Signed date",
        tracking=True
    )
    sign_signature = fields.Binary(
        string="Digital Signature",
        groups=False
    )
    position = fields.Selection([
        ("top", "Top"),
        ("footer", "Footer"), ],
        string="Signature Position",
        default="footer"
    )
    x_coord = fields.Float(string="Position X")
    y_coord = fields.Float(string="Position Y")

    def _compute_user_ids(self):
        for record in self:
            domain = [('share', '=', False)]
            record.user_ids = self.env["res.users"].search(domain)

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.user_id.name} - {record.role_id.name if record.role_id else ''}"


    @staticmethod
    def attach_signature_to_pdf(pdf_binary_base64, signature_image_base64, approval_type, x=None, y=None):
        """Adjunta una firma en un cuadrante específico de la última página."""

        # Si no se pasa x, y, usar cuadrante 3 por defecto
        if x is None or y is None:
            quadrant_positions = {
                1: (width - 150, height - 100),
                2: (50, height - 100),
                3: (width - 150, 50),
                4: (50, 50),
            }
            x, y = quadrant_positions.get(3)

        if not pdf_binary_base64 or not signature_image_base64:
            return pdf_binary_base64  # Si falta algo, no modificamos

            # Decodificar los datos binarios
        pdf_data = base64.b64decode(pdf_binary_base64)
        signature_image = base64.b64decode(signature_image_base64)

        # Leer el PDF original
        original_pdf = PdfFileReader(io.BytesIO(pdf_data))

        # Buscar última página válida
        # last_page = None
        # last_page_index = None
        # for idx in reversed(range(original_pdf.numPages)):
        #     page = original_pdf.getPage(idx)
        #     try:
        #         if hasattr(page, "mediaBox") and len(page.mediaBox) == 4:
        #             last_page = page
        #             last_page_index = idx
        #             break
        #     except Exception:
        #         continue

        # SIEMPRE usar la primera página
        page_index = 0
        page = original_pdf.getPage(0)

        try:
            width = float(page.mediaBox.getWidth())
            height = float(page.mediaBox.getHeight())
        except Exception:
            width, height = 595, 842  # A4

        # Si no hay página válida, usar primera
        # if last_page is None:
        #     last_page = original_pdf.getPage(0)
        #     last_page_index = 0
        #     width, height = 595, 842  # tamaño A4 por defecto
        # else:
        #     try:
        #         width = float(last_page.mediaBox.getWidth())
        #         height = float(last_page.mediaBox.getHeight())
        #     except Exception:
        #         width, height = 595, 842

        # Configurar posiciones de cuadrantes
        quadrant_positions = {
            1: (width - 150, height - 100),  # arriba derecha
            2: (50, height - 100),  # arriba izquierda
            3: (width - 150, 50),  # abajo derecha
            4: (50, 50),  # abajo izquierda
        }

        # Obtener coordenadas según el cuadrante
       # x, y = quadrant_positions.get(quadrant, quadrant_positions[4])
        sig_width, sig_height = 80, 35

        # Crear PDF con la nueva firma
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))

        # Dibujar la firma (sin borrar lo anterior)
        can.drawImage(ImageReader(io.BytesIO(signature_image)), x, y,
                      width=sig_width, height=sig_height, mask="auto")

        # Agregar texto debajo de la firma
        text_x = x
        text_y = y - 12  # 12 puntos debajo de la firma
        can.setFont("Helvetica", 10)
        can.setFillColor(colors.black)
        if approval_type == "approver":
            can.drawString(text_x, text_y, f"Aprobado por:")
        elif approval_type == "reviewer":
            can.drawString(text_x, text_y, f"Revisado por:")

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
