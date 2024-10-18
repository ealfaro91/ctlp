# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HelpdeskTicketType(models.Model):
    _inherit = "helpdesk.ticket.type"

    @api.depends('area_id', 'name')
    def _compute_display_name(self):
        for type in self:
            type.display_name = f'{type.name} - {type.area_id.name}'

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
