# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicketTeam(models.Model):
    _name = "helpdesk.ticket.team"
    _inherit = ["helpdesk.ticket.team",  "avatar.mixin"]

    area_id = fields.Many2one(
        "helpdesk.ticket.area", string="Area",
        required=True, tracking=True
    )
    color = fields.Integer(
        string="Color Index", related="area_id.color",
        tracking=True, store=True
    )



