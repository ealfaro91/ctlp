from odoo import models, fields, api, _


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

    def button_send_approval_request(self):
        self.ensure_one()

    document_file_type_id = fields.Many2one(
        comodel_name="document.file.type",
        string="Document File Type",
        help="The type of the document file, used to categorize and manage different file types.",
        tracking=True
    )
    reviewer_id = fields.Many2one(
        comodel_name="res.users",
        string="Reviewer",
        help="The user responsible for reviewing the document.",
        tracking=True
    )
    approver_id = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        help="The user responsible for approving the document.",
        tracking=True
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
         ('private', 'Privado'), ('public', 'Public')],
         string='Tipo de privacidad',
        default='private',
     )
    published = fields.Boolean(
        string='Publicado',
        default=False,
        help="Indicates whether the document is published or not."
    )

    area_id = fields.Many2one(
        comodel_name='helpdesk.ticket.area',
        string='Area',
        help="The area associated with the document, used for categorization and management.",
        tracking=True
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


    # def button_send_approval_request(self):
    #     """Send approval request emails to all users in the approval log."""
    #     for rec in self:
    #         if not rec.approval_log_ids:
    #             raise ValidationError(
    #                 _("There are no users in the approval log to send the request.")
    #             )
    #         for user in rec.approval_log_ids.mapped("user_id"):
    #             mail_template = self.env.ref(
    #                 "project_bol.fsn_approval_email", raise_if_not_found=True
    #             )
    #             mail_template.send_mail(
    #                 rec.id, force_send=False, raise_exception=True
    #             )
    #         rec.sent_approval_request = True
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'message': _("The approval request has been sent successfully."),
    #                 'next': {'type': 'ir.actions.act_window_close'},
    #                 'sticky': False,
    #                 'type': 'success',
    #             }}
