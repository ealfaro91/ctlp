# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketCategory(models.Model):
    _name = "helpdesk.ticket.category"
    _order = "sequence,name"
    _inherit = ["mail.thread", "mail.activity.mixin", "helpdesk.ticket.category"]


    type_id = fields.Many2one(
        "helpdesk.ticket.type",
        string="Tipo ticket",
        required=True,
        tracking=True
    )
    user_id = fields.Many2one(
        "res.users", string="Responsible", required=True, tracking=True,
        )



