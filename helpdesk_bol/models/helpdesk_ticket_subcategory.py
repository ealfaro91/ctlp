# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketSubCategory(models.Model):
    _name = "helpdesk.ticket.subcategory"
    _order = "sequence,name"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Sub-Category")
    category_id = fields.Many2one(
        "helpdesk.ticket.category",
        string="Category",
        required=True,
        tracking=True
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10
    )
    max_attention_time = fields.Integer(string="Max attention time", tracking=True)
    user_id = fields.Many2one("res.users", string="User", tracking=True)

