# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HelpdeskTicketLocation(models.Model):
    _name = "helpdesk.ticket.location"
    _description = "Helpdesk Ticket Location"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.onchange('area_id')
    def _onchange_area_id(self):
        self.category_id = False

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Location", tracking=True, translate=True)
    category_id = fields.Many2one(
        "helpdesk.ticket.category", string="Category",
        tracking=True, domain="[('area_id', '=', area_id)]"
    )
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        tracking=True,
        store=True
    )

