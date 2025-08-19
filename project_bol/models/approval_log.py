
from odoo import api, fields , models


class ApprovalLog(models.Model):
    _inherit = "approval.log"

    def _get_role_domain(self):
        return [
            ('category_id', '=', self.env.ref("project_bol.module_fsn_category").id)
        ]

    def _get_user_domain(self):
        return [
            ('groups_id', 'in', self.role_id.id)
        ]

    project_fsn_id = fields.Many2one(
        "project.fsn",
        string="Project FSN",
        help="Needs Request Form related to this approval log.",
        tracking=True,
    )

    def _signed(self):
        """ Calls the method to attach the signature to the PDF document. """
        new_pdf = self.attach_signature_to_pdf(self.project_fsn_id.document, self.user_id.sign_signature)
        self.project_fsn_id.document_signed = new_pdf

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.user_id.name} - {record.role_id.name if record.role_id else ''}"

