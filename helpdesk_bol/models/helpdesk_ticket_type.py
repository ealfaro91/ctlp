# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketType(models.Model):
    _name = "helpdesk.ticket.type"
    _inherit = ["mail.thread", "mail.activity.mixin", "helpdesk.ticket.type"]

    category_ids = fields.One2many("helpdesk.ticket.category", "type_id", string="Categories")
    color = fields.Integer(string="Color", default=1)

