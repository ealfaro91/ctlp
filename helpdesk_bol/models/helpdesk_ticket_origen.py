# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HelpdeskTicketOrigen(models.Model):
    _name = "helpdesk.ticket.origen"
    _description = "Helpdesk Ticket Origen"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Origen", tracking=True, translate=True)
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        tracking=True,
        required=True
    )

