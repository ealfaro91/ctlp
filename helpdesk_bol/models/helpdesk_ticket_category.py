# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketCategory(models.Model):
    _inherit = "helpdesk.ticket.category"
    _order = "sequence,name"

    type_id = fields.Many2one(
        "helpdesk.ticket.type",
        string="Tipo ticket",
        required=True,
        tracking=True
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=True,
        tracking=True,
    )



