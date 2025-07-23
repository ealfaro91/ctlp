

from odoo import api, fields , models


class ApprovalState(models.Model):
    _name = "approval.state"
    _description = "Approval state"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence"

    name = fields.Char(string="Name", required=True, tracking=True, translate=True)
    role_id = fields.Many2one("res.groups", string="Role", tracking=True)
    sequence = fields.Integer(string="Sequence", required=True, tracking=True)
    model_id = fields.Many2one("ir.model", string="Module", tracking=True)
    user_id = fields.Many2one("res.users", string="User", tracking=True, store=True, compute="_compute_user_id")
    last_approval_role = fields.Boolean(string="Last approval role", tracking=True)
    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
        domain=[("model_id", "=", "model_id")],
        help="If set an email will be sent to the "
             "customer when the ticket"
             "reaches this step.",
        tracking=True
    )

    def _compute_user_id(self):
        for state in self:
            state.user_id = False
            if state.role_id.users:
                state.user_id = state.role_id.users[0].id
