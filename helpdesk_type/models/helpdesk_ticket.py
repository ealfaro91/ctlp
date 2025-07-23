
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    type_id = fields.Many2one(
        "helpdesk.ticket.type",
        string="Requirement type",
        tracking=True
    )
