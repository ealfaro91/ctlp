# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketArea(models.Model):
    _name = "helpdesk.ticket.area"
    _description = "Helpdesk Ticket Area"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin",]
    _sql_constraints = [("code_uniq", "unique(code)",  "Area code must be unique",)]

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Area", tracking=True, translate=True)
    code = fields.Char(string="Code", tracking=True)
    type_ids = fields.One2many("helpdesk.ticket.type", "area_id", string="Types", tracking=True)
    color = fields.Integer(string="Color Index", default=0, tracking=True)

