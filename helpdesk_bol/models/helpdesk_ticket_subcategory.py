# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketSubCategory(models.Model):
    _name = "helpdesk.ticket.subcategory"
    _order = "sequence,name"
    _inherit = ["mail.thread", "mail.activity.mixin",]

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Sub-Category", required=True, tracking=True)
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
    max_attention_time = fields.Float(string="Max attention time (hours)", tracking=True)

