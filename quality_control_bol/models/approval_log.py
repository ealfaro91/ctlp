
from odoo import api, fields , models


class ApprovalLog(models.Model):
    _inherit = "approval.log"

    attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Attachment",
        help="The attachment related to this approval log.",
        tracking=True,
    )

    def _signed(self):
        """ Calls the method to attach the signature to the PDF document. """
        new_pdf = self.attach_signature_to_pdf(self.attachment_id.datas, self.user_id.sign_signature)
        self.attachment_id.document_signed = new_pdf

