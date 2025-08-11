
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
    sequence = fields.Integer(string="Sequence", required=True, tracking=True)
    role_id = fields.Many2one("res.groups", string="Role", tracking=True)
    user_id = fields.Many2one("res.users", string="User", domain="[('groups_id', 'in', role_id)]")
    image = fields.Binary(
        string="Image",
        related="user_id.image_1920",
        readonly=True,
        help="Image of the user who made the approval."
    )
    state = fields.Selection([
        ("without_approval", "Not approved yet"),
        ("approved", "Approved")]
    )

    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    sign_signature = fields.Binary(string="Digital Signature", groups=False)
    last_approval_role = fields.Boolean(string="Last approval role")
    project_fsn_id = fields.Many2one(
        "project.fsn",
        string="Project FSN",
        help="Needs Request Form related to this approval log.",
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
