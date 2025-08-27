from odoo import models, fields, api, _


import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfFileReader, PdfFileWriter  # 👈 API vieja



class IrAttachment(models.Model):
    _name = "ir.attachment"
    _inherit = ["ir.attachment", "mail.thread", "mail.activity.mixin", "portal.mixin"]

    def button_publish_document(self):
        """Publish the document, making it accessible to the public."""
        self.ensure_one()
        if not self.published:
            self.published = True
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("El documento ha sido publicado."),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("El documento ya está publicado."),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'warning',
                }
            }

    @staticmethod
    def attach_signature_to_pdf(pdf_binary_base64, signature_image_base64, quadrant=1):
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
        x, y = quadrant_positions.get(quadrant, quadrant_positions[1])
        sig_width, sig_height = 120, 50

        # Crear PDF con la firma
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))
        can.setFillColor(colors.white)
        can.rect(x, y, sig_width, sig_height, fill=1, stroke=0)
        can.drawImage(ImageReader(io.BytesIO(signature_image)), x, y,
                      width=sig_width, height=sig_height, mask='auto')

        # Agregar texto debajo de la firma
        text_x = x
        text_y = y - 12  # 12 puntos debajo de la firma
        can.setFont("Helvetica", 10)
        can.setFillColor(colors.black)
        can.drawString(text_x, text_y, f"Elaborado por:")
        can.save()

        # Fusionar firma con la última página
        packet.seek(0)
        signature_pdf = PdfFileReader(packet)
        writer = PdfFileWriter()

        for i in range(original_pdf.numPages):
            page = original_pdf.getPage(i)
            if i == last_page_index:
                page.mergePage(signature_pdf.getPage(0))  # 👈 API vieja
            writer.addPage(page)

        # Guardar PDF final
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        return base64.b64encode(output_stream.read())

    def button_send_reviewer_request(self):
        mail_template = self.env.ref(
            "quality_control_bol.document_approval_email", raise_if_not_found=True
        )
        mail_template.send_mail(
            self.id, force_send=False, raise_exception=True
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _("Se ha enviado para revisión."),
                'next': {'type': 'ir.actions.act_window_close'},
                'sticky': False,
                'type': 'success',
            }
        }
    signed_by_author = fields.Boolean(
        string="Signed by Author",
        default=False,
        help="Indicates whether the document has been signed by the author."
    )
    sent_approval_request = fields.Boolean(
        string="Sent Approval Request",
        default=False,
        help="Indicates whether the approval request has been sent."
    )
    def button_author_sign(self):
        """ Calls the method to attach the signature to the PDF document. """
        new_pdf = self.attach_signature_to_pdf(self.datas, self.create_uid.sign_signature)
        self.document_signed = new_pdf
        self.signed_by_author = True



    @api.onchange('document_directory_id')
    def _onchange_user_ids(self):
        for rec in self:
            rec.user_ids = False
            if rec.document_directory_id:
                rec.user_ids = rec.document_directory_id.user_ids

    user_ids = fields.Many2many(
        "res.users",
        string="Usuarios permitidos",
        related=False,
        readonly=False
    )
    document_file_type_id = fields.Many2one(
        comodel_name="document.file.type",
        string="Document File Type",
        help="The type of the document file, used to categorize and manage different file types.",
      #  domain="[('document_directory_ids', 'in', document_directory_id)]",
        tracking=True
    )
    document_file_type_ids = fields.Many2many(
        comodel_name="document.file.type",
        string="Document File Types",
        related="document_directory_id.document_file_type_ids",
        help="The types of document files associated with the selected directory.",
        readonly=True
    )
    approval_log_ids = fields.One2many(
        comodel_name="approval.log",
        inverse_name="attachment_id",
        string="Approvers",
    )
    reviewer_ids = fields.One2many(
        comodel_name="approval.log",
        inverse_name="document_id",
        string="Reviewers",
    )
    version_id = fields.Many2one(
        comodel_name='document.version',
        string='Document Version',
        help="The version of the document attachment.",
        tracking=True
    )
    version_ids = fields.One2many(
        comodel_name='document.version',
        inverse_name='attachment_id',
        string='Document Versions',
        help="List of versions for this document attachment.",
    )
    # obsolete = fields.Boolean(
    #     string='Obsolete',
    #     default=False,
    #     help="Indicates whether the document is obsolete."
    # )
    state = fields.Selection([
        ('to_review', 'To Review'),
        ('reviewed', 'Reviewed'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('published', 'Published')],
        string='Estado',
        default='to_review'
    )
    privacy_type = fields.Selection([
         ('private', 'Private'), ('public', 'Public')],
         string='Tipo de privacidad',
        default='private',
        required=True,
    )
    area_id = fields.Many2one(
        comodel_name='helpdesk.ticket.area',
        string='Area',
        help="The area associated with the document, used for categorization and management.",
        tracking=True,
        related="document_directory_id.area_id",
    )
    document_signed = fields.Binary(
        string="Signed Document",
        attachment=True,
    )
    document_signed_filename = fields.Char(
        string="Document Signed File Name",
        tracking=True
    )
    document_url = fields.Char(
        compute="get_document_url", string="Portal Access Link"
    )

    def get_document_url(self):
        """Generate the URL for the document in the portal."""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            if not rec.access_token:
                rec._portal_ensure_token()
            rec.document_url = "%s/my/document/%s?access_token=%s" % (
                base_url,
                rec.id,
                rec.access_token,
            )

    def _get_portal_return_action(self):
        """Return the action used to display record when returning from customer portal."""
        self.ensure_one()
        return self.env.ref("project_bol.approval_log_action")

    def get_portal_sign_url(self):
        return "/my/document/%s/sign?access_token=%s" % (self.id, self.access_token)


    def button_send_approval_request(self):
        """Send approval request emails to all users in the approval log."""
        for rec in self:
            if not rec.reviewer_ids:
                raise ValidationError(
                    _("There are no users in the approval log to send the request.")
                )
            if not rec.approval_log_ids:
                raise ValidationError(
                    _("There are no users in the approval log to send the request.")
                )
            for user in rec.approval_log_ids.mapped("user_id") + rec.reviewer_ids.mapped("user_id"):
                mail_template = self.env.ref(
                    "quality_control_bol.document_approval_email", raise_if_not_found=True
                )
                mail_template.send_mail(
                    rec.id, force_send=False, raise_exception=True
                )
            rec.sent_approval_request = True
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("The approval request has been sent successfully."),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'success',
                }}
