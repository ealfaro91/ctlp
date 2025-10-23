
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
        required=True,
        tracking=True,
        domain=[("share", "=", False)]
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
        [("reviewer", "Reviewer"), ("approver", "Approver")],
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
    sign_signature = fields.Binary(string="Digital Signature", groups=False)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     records = super().create(vals_list)
    #     for record in records:
    #         record._compute_signature_position()
    #     return records
    #
    # def _compute_signature_position(self):
    #     """ Compute the signature position for this approval log"""
    #     width, height = 595, 842  # tamaño A4 por defecto
    #     sig_width, sig_height = 80, 35
    #     margin_x, margin_y = 50, 40
    #     spacing_y = 25  # espacio entre filas
    #
    #     # calcular índice basado en el orden en parent_id
    #     index = self.parent_id.approval_log_ids.ids.index(self.id)
    #
    #     # solo abajo: izq/der
    #     max_per_row = 2
    #     row = index // max_per_row
    #     col = index % max_per_row
    #
    #     if col == 0:
    #         x = margin_x
    #     else:
    #         x = width - margin_x - sig_width
    #
    #     y = margin_y + row * (sig_height + spacing_y)
    #
    #     self.write({
    #         "x_coord": x,
    #         "y_coord": y,
    #         "sequence": index,
    #     })

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.user_id.name} - {record.role_id.name if record.role_id else ''}"

