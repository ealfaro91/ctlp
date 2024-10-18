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
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        related="type_id.area_id",
        tracking=True,
        store=True
    )
    color = fields.Integer(
        string="Color Index", related="area_id.color",
        tracking=True, store=True
    )



