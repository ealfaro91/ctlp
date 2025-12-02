
from odoo import api, fields , models


class ApprovalLog(models.Model):
    _name = "approval.log"
    _description = "Approval log"
    _inherit = ["document.signature.mixin"]
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
        required=True,
        tracking=True,
        domain="[('share', '=', False)]"
    #    domain="[('id', 'in', user_ids)]",
    )
    user_ids = fields.Many2many(
        "res.users",
        string="Users",
        compute="_compute_user_ids",
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
    approval_type = fields.Selection(
        [("author", "Author"),
         ("reviewer", "Reviewer"),
         ("approver", "Approver")],
        string="Approval Type",
        default="approver",
        tracking=True
    )
    request_sign_date = fields.Datetime(
        string="Request sign date",
        tracking=True
    )
    signed_date = fields.Datetime(
        string="Signed date",
        tracking=True
    )
    sign_signature = fields.Binary(
        string="Digital Signature",
        groups=False
    )

    def _compute_user_ids(self):
        for record in self:
            domain = [('share', '=', False)]
            record.user_ids = self.env["res.users"].search(domain)

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.user_id.name} - {record.role_id.name if record.role_id else ''}"

