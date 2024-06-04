# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketArea(models.Model):
    _name = "helpdesk.ticket.area"
    _order = "sequence,name"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Area")
    area_type = fields.Selection([('TI', 'TI')], string="Area")
