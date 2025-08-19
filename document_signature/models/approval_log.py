
from odoo import api, fields , models


class ApprovalLog(models.Model):
    _name = "approval.log"
    _description = "Approval log"
    _inherit = ["mail.thread", "mail.activity.mixin", "document.signature.mixin"]
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

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.user_id.name} - {record.role_id.name if record.role_id else ''}"

