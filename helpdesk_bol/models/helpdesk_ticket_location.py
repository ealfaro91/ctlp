# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HelpdeskTicketLocation(models.Model):
    _name = "helpdesk.ticket.location"
    _description = "Helpdesk Ticket Location"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Location", tracking=True, translate=True)
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        tracking=True,
        store=True
    )

