
from odoo import api, fields , models


class ApprovalLog(models.Model):
    _inherit = "approval.log"

    def _get_role_domain(self):
        return [
            ('category_id', '=', self.env.ref("project_bol.module_fsn_category").id)
        ]

    # def _get_user_domain(self):
    #     domain = [("share", "=", False)]
    #     if fsn_id:
    #         log_ids = fsn_id.approval_log_ids
    #         domain.extend(('groups_id', 'in', self.role_id.id), ('id', 'not in', log_ids.mapped("user_id")) )
    #         return domain
    #     return domain

    role_id = fields.Many2one(
        domain=lambda self: self._get_role_domain(),
    )
    # user_id = fields.Many2one(
    #     domain="[('id', 'in', user_ids)]",
    # )
    # user_ids = fields.Many2many(
    #     "res.users",
    #     string="Users",
    #     compute="_compute_user_ids",
    # )
    project_fsn_id = fields.Many2one(
        "project.fsn",
        string="Project FSN",
    )

    # def _compute_user_ids(self):
    #     for record in self:
    #         fsn_id = record.project_fsn_id or self.env["project.fsn"].browse(self.env.context.get("default_project_fsn_id"))
    #         domain = [('share', '=', False)]
    #         if fsn_id:
    #             log_ids = fsn_id.approval_log_ids
    #             domain.extend(('groups_id', 'in', self.role_id.id), ('id', 'not in', log_ids.mapped("user_id")))
    #         record.user_ids = self.env["res.users"].search(domain)

    def _signed(self):
        """ Calls the method to attach the signature to the PDF document. """
        new_pdf = self.attach_signature_to_pdf(self.project_fsn_id.document_signed, self.user_id.sign_signature)
        self.project_fsn_id.document_signed = new_pdf


