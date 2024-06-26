# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketType(models.Model):
    _inherit = "helpdesk.ticket.type"

    category_ids = fields.One2many(
        "helpdesk.ticket.category", "type_id",
        string="Categories", 
        tracking=True
    )
    color = fields.Integer(string="Color", default=1, tracking=True)

