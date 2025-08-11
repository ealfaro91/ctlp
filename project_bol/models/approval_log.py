
from odoo import api, fields , models


class ApprovalLog(models.Model):
    _name = "approval.log"
    _description = "Approval log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _rec_name = "role_id"

    def _get_role_domain(self):
        return [
            ('category_id', '=', self.env.ref("project_bol.module_fsn_category").id)
        ]

    def _get_user_domain(self):
        return [
            ('groups_id', 'in', self.role_id.id)
        ]

    sequence = fields.Integer(
        string="Sequence",
        required=False,
        tracking=True
    )
    role_id = fields.Many2one(
        "res.groups",
        string="Role",
        domain=_get_role_domain,
        tracking=True
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
       # domain=_get_user_domain
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
    request_sign_date = fields.Datetime(string="Request sign date")
    signed_date = fields.Datetime(string="Signed date")
    sign_signature = fields.Binary(string="Digital Signature", groups=False)
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
