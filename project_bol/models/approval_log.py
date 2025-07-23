
from odoo import api, fields , models


class ApprovalLog(models.Model):
    _name = "approval.log"
    _description = "Approval log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
        tracking=True,
    )
    user_id = fields.Many2one("res.users", string="User", default=lambda self: self.env.user)
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    sign_signature = fields.Binary(string="Digital Signature", groups=False)
    role_id = fields.Many2one(
        "res.groups", string="Role",
    )
    last_approval_role = fields.Boolean(string="Last approval role")
    project_fsn_id = fields.Many2one(
        "project.fsn",
        string="Project FSN",
        help="Functional Specification Note related to this approval log.",
        tracking=True,
    )

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.user_id.name} - {record.role_id.name}"

    #
    # @api.model
    # def create(self, vals):
    #     if vals.get('mrp_production_id'):
    #         last_log = self.search([
    #             ('mrp_production_id', '=', vals['mrp_production_id'])
    #         ], order='sequence desc', limit=1)
    #         vals['sequence'] = last_log.sequence + 1 if last_log else 1
    #     return super(ApprovalOrderLog, self).create(vals)
