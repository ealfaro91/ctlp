# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HelpdeskTicketCategory(models.Model):
    _inherit = "helpdesk.ticket.category"
    _order = "sequence,name"

    @api.onchange('area_id')
    def _onchange_area_id(self):
        self.type_id = False

    type_id = fields.Many2one(
        "helpdesk.ticket.type",
        string="Tipo ticket",
        required=True,
        tracking=True,
        domain="[('area_id', '=', area_id)]"
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=True,
        tracking=True,
    )
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        tracking=True,
        required=True
    )
    color = fields.Integer(
        string="Color Index", related="area_id.color",
        tracking=True, store=True
    )



