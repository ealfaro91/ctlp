# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketLocation(models.Model):
    _name = "helpdesk.ticket.location"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin",]

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Location", tracking=True, translate=True)
    category_id = fields.Many2one("helpdesk.ticket.category", string="Category", tracking=True)
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        related="category_id.area_id",
        tracking=True,
        store=True
    )

