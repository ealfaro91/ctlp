# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HelpdeskTicketType(models.Model):
    _inherit = "helpdesk.ticket.type"

    area_id = fields.Many2one(
        "helpdesk.ticket.area", string="Area",
        tracking=True, required=True
    )
    category_ids = fields.One2many(
        "helpdesk.ticket.category", "type_id",
        string="Categories",
        tracking=True
    )
    color = fields.Integer(
        string="Color Index", related="area_id.color",
        tracking=True, store=True
    )
