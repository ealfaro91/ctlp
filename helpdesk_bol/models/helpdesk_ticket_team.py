# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    area_id = fields.Many2one(
        "helpdesk.ticket.area", string="Area",
        required=True, tracking=True
    )
    color = fields.Integer(
        string="Color Index", related="area_id.color",
        tracking=True, store=True
    )



