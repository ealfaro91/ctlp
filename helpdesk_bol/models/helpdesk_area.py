# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketArea(models.Model):
    _name = "helpdesk.ticket.area"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin",]


    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Area", tracking=True)
    area_type = fields.Selection([('TI', 'TI')], string="Area", tracking=True)
