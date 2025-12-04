from odoo import models, fields, api, _

from odoo.exceptions import ValidationError


import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfFileReader, PdfFileWriter  # 👈 API vieja


class IrAttachment(models.Model):
    _name = "ir.attachment"
    _inherit = ["ir.attachment", "mail.thread", "mail.activity.mixin", "portal.mixin"]

    # active = fields.Boolean(
    #     string="Active",
    #     default=True,
    # )
    #URGENTE MIGRATION DEL CAMPO ACTIVE

    signed_by_author = fields.Boolean(
        string="Signed by Author",
        default=False,
        tracking=True,
        help="Indicates whether the document has been signed by the author."
    )
    sent_approval_request = fields.Boolean(
        string="Sent Approval Request",
        default=False,
        tracking=True,
        help="Indicates whether the approval request has been sent."
    )
    published = fields.Boolean(
        string="Publicado",
        default=False,
        tracking=True,
    )
    user_ids = fields.Many2many(
        "res.users",
        string="Usuarios permitidos",
        related=False,
        readonly=False,
        domain="[('id','in', allowed_user_ids)]"
    )
    allowed_user_ids = fields.Many2many(
        "res.users",
        string="Usuarios permitidos",
        related="document_directory_id.user_ids"
    )
    document_file_type_id = fields.Many2one(
        comodel_name="document.file.type",
        string="Document File Type",
        help="The type of the document file, used to categorize and manage different file types.",
        domain="[('parent_type_id', '=', False)]",
        tracking=True
    )
    child_type_id = fields.Many2one(
        comodel_name="document.file.type",
        string="Subcategory file type",
        domain="[('parent_type_id', '=', document_file_type_id)]",
        tracking=True,
    )
    has_subcategories = fields.Boolean(
        string='Has Subcategories',
        related="document_file_type_id.has_subcategories",
        store=True,
        readonly=True
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
    version_id = fields.Many2one(
        comodel_name='document.version',
        string='Document Version',
        domain="[('active', '=', True)]",
        help="The version of the document attachment.",
        tracking=True
    )
    version_ids = fields.One2many(
        comodel_name='document.version',
        inverse_name='attachment_id',
        string='Document Versions',
        context={"active_test": False},
        help="List of versions for this document attachment.",
    )
    attachment_review_request_ids = fields.One2many(
        comodel_name='attachment.review.request',
        inverse_name='attachment_id',
        string='Attachment Review Request',
        help="The attachment review request associated with the document attachment.",
    )
    obsolete = fields.Boolean(
        string='Obsolete',
        default=False,
        store=True,
        compute='_compute_obsolete',
    )
    state = fields.Selection([
        ('to_review', 'To Review'),
        ('reviewed', 'Reviewed'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('published', 'Published')],
        string='Estado',
        default='to_review',
        compute='_compute_approval_state',
        inverse='_inverse_compute_approval_state',
     #   store=True
    )
    privacy_type = fields.Selection([
         ('private', 'Private'), ('public', 'Public')],
         string='Tipo de privacidad',
        default='private',
        required=True,
        tracking=True,
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

    def request_review(self):
        for rec in self:
            rec.attachment_review_request_ids.create({
                'user_id': self.env.user.id,
                'attachment_id': rec.id,
                'date': fields.Datetime.now(),
                'version_id': rec.version_id.id,
                'message': 'Solicitud de revisión',
            })
            rec.state = 'to_review'

    def button_replace_version(self):
        self.version_id.active = False
        self.active = False

    @api.depends('version_id.deactivate_date', 'version_id')
    def _compute_obsolete(self):
        for rec in self:
            rec.obsolete = any(version.deactivate_date for version in rec.version_ids)
    #
    # def _inverse_compute_approval_state(self):
    #     """Inverse method to set the state of the FSN based on the approval log."""
    #     for fsn in self:
    #         fsn.state = "to_review"
    #         if all(log.state == "approved" for log in fsn.approval_log_ids):
    #             fsn.state = "approved"
    #
            #     fsn.sent_approval_request = False
            # elif fsn.state == "to_approve":
            #     fsn.sent_approval_request = True
            # elif fsn.state == "approved":
            #     fsn.sent_approval_request = True
            # elif fsn.state == "cancelled":
            #     fsn.sent_approval_request = False
            # elif fsn.state == "cancelled":
            #     fsn.sent_approval_request = False

    def _inverse_compute_approval_state(self):
        for fsn in self:
            fsn.state = "to_review"
            if fsn.approval_log_ids:
                if fsn.sent_approval_request and not all(log.state == "approved" for log in fsn.approval_log_ids):
                    fsn.state = "to_approve"

    @api.depends("approval_log_ids", "sent_approval_request", "approval_log_ids.state", "published")
    def _compute_approval_state(self):
        """Compute the approval state based on the approval
         log and create a project if all approvals are done."""
        for fsn in self:
            fsn.state = "to_review"
            if fsn.approval_log_ids:
                if fsn.sent_approval_request and not all(log.state == "approved" for log in fsn.approval_log_ids):
                    fsn.state = "to_approve"
                if all(log.state == "approved" for log in fsn.approval_log_ids):
                    fsn.state = "approved"
                if fsn.published:
                    fsn.state = "published"
            # fsn.state = "approval_request" if fsn.sent_approval_request and not all(
            #     log.state == "approved" for log in fsn.approval_log_ids
            # ) else "to_approve"
            # if fsn.approval_log_ids:
            #     if all(log.state == "approved" for log in fsn.approval_log_ids):
            #         fsn.state = "approved"
            #     if fsn.state == "approved":
            #         mail_template = self.env.ref(
            #             "project_bol.fsn_approved_notification", raise_if_not_found=True
            #         )
            #         mail_template.sudo().send_mail(fsn.id, force_send=False, raise_exception=True)
            #         fsn._action_create_project()

    def button_publish_document(self):
        """Publish the document, making it accessible to the public."""
        self.ensure_one()
        self.published = True
        for user in self.user_ids + self.approval_log_ids.mapped("user_id"):
            mail_template = self.env.ref(
                "quality_control_bol.document_published_notification", raise_if_not_found=True
            )
            mail_template.write({"email_to": user.email})
            mail_template.send_mail(
                self.id, force_send=False, raise_exception=True
            )
        self.state = 'published'
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
        return self.env.ref("document_signature.approval_log_action")

    def get_portal_sign_url(self):
        return "/my/document/%s/sign?access_token=%s" % (self.id, self.access_token)

    def button_send_approval_request(self):
        """Send approval request emails to all users in the approval log."""
        for rec in self:
            if not rec.approval_log_ids:
                raise ValidationError(
                    _("There are no users in the approval log to send the request.")
                )
            rec.assign_signature_coords(rec.approval_log_ids)
            for user in rec.approval_log_ids.mapped("user_id"):
                mail_template = self.env.ref(
                    "quality_control_bol.document_approval_email", raise_if_not_found=True
                )
                # Aquí estamos pasando al contexto el usuario
                mail_template.write({"email_to": user.email})
                mail_template.sudo().with_context(
                    user_name=user.name,
                ).send_mail(
                    rec.id, force_send=False, raise_exception=True
                )
            for log in rec.approval_log_ids:
                log.request_sign_date = fields.Datetime.now()
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

    @staticmethod
    def assign_signature_coords(approval_logs, page_width=595, base_y=800):
        """
        Assign signature coordinates in a table at the top of the page.
        Columns: author (left), reviewer (center), approver (right).
        Multiple rows if needed.
        """
        sig_width, sig_height = 80, 35
        margin_y = 40

        # columnas
        col_author = 50
        col_reviewer = (page_width / 2) - (sig_width / 2)
        col_approver = page_width - sig_width - 50

        columns_x = {
            "author": col_author,
            "reviewer": col_reviewer,
            "approver": col_approver,
        }

        # cómo se apilan verticalmente dentro de cada columna
        row_counter = {
            "author": 0,
            "reviewer": 0,
            "approver": 0,
        }

        for log in approval_logs:
            t = log.approval_type or "author"
            if t not in columns_x:
                t = "author"

            x = columns_x[t]
            y = base_y - row_counter[t] * (sig_height + margin_y)

            log.write({
                "x_coord": x,
                "y_coord": y
            })

            row_counter[t] += 1

    @staticmethod
    def attach_signature_to_pdf(pdf_binary_base64, signature, approval_logs):
        """
        Adjunta firmas en PDF A4:
        - Firma elaborador a la izquierda
        - Columnas de reviewer y approver a la derecha de la firma elaborador
        - Firmas se apilan verticalmente sin solaparse
        """
        if not pdf_binary_base64:
            return pdf_binary_base64

        pdf_data = base64.b64decode(pdf_binary_base64)
        original_pdf = PdfFileReader(io.BytesIO(pdf_data))

        # Última página válida
        last_page_index = None
        for idx in reversed(range(original_pdf.numPages)):
            page = original_pdf.getPage(idx)
            try:
                if hasattr(page, "mediaBox") and len(page.mediaBox) == 4:
                    last_page_index = idx
                    width = float(page.mediaBox.getWidth())
                    height = float(page.mediaBox.getHeight())
                    break
            except Exception:
                continue
        if last_page_index is None:
            last_page_index = 0
            width, height = 595, 842

        # Separar logs por tipo
        reviewers = [log for log in approval_logs if log.approval_type == 'reviewer']
        approvers = [log for log in approval_logs if log.approval_type == 'approver']

        # Configuración
        sig_width, sig_height = 80, 35
        margin_y = 20
        base_y = height - 100  # desde la parte superior
        base_x_elab = 50  # firma elaborador
        base_x_review = base_x_elab + sig_width + 50  # columna reviewer
        base_x_approve = base_x_review + sig_width + 50  # columna approver

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))

        # Dibujar firma elaborador
        if signature:
            sig_elab = base64.b64decode(signature)
            can.drawImage(ImageReader(io.BytesIO(sig_elab)), base_x_elab, base_y,
                          width=sig_width, height=sig_height, mask='auto')
            can.setFont("Helvetica", 10)
            can.setFillColor(colors.black)
            can.drawString(base_x_elab, base_y - 12, "Elaborado por:")

        # Función para dibujar columnas
        def draw_column(logs, base_x, label):
            for i, log in enumerate(logs):
                x = base_x
                y = base_y - i * (sig_height + margin_y)
                sig_img = base64.b64decode(log.signature_image)
                can.drawImage(ImageReader(io.BytesIO(sig_img)), x, y,
                              width=sig_width, height=sig_height, mask='auto')
                can.setFont("Helvetica", 10)
                can.setFillColor(colors.black)
                can.drawString(x, y - 12, f"{label}:")

        draw_column(reviewers, base_x_review, "Revisado por")
        draw_column(approvers, base_x_approve, "Aprobado por")

        can.save()

        # Fusionar con PDF original
        packet.seek(0)
        signature_pdf = PdfFileReader(packet)
        writer = PdfFileWriter()
        for i in range(original_pdf.numPages):
            page = original_pdf.getPage(i)
            if i == last_page_index:
                page.mergePage(signature_pdf.getPage(0))
            writer.addPage(page)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return base64.b64encode(output_stream.read())

    def button_author_sign(self):
        """ Calls the method to attach the signature to the PDF document. """
        if not self.env.user.sign_signature:
            raise ValidationError(_("The author signature is required. Go to the user settings to add it."))
        self.approval_log_ids.create({
            'attachment_id': self.id,
            'user_id': self.env.user.id,
            'signed_date': fields.Datetime.now(),
            'sign_signature': self.env.user.sign_signature,
            'approval_type': 'author',
        })  # Asignar coordenadas a todos los logs, incluyendo este
        self.assign_signature_coords(self.approval_log_ids)
        new_pdf = self.attach_signature_to_pdf(self.datas, self.env.user.sign_signature, self.approval_log_ids)
        self.document_signed = new_pdf
        self.signed_by_author = True
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": _("The Document has been signed by the author."),
                "next": {"type": "ir.actions.act_window_close"},
                "sticky": False,
                "type": "success",
            }
        }
