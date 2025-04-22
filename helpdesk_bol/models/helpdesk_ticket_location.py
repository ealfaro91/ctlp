# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HelpdeskTicketLocation(models.Model):
    _name = "helpdesk.ticket.location"
    _description = "Helpdesk Ticket Location"
    _order = "sequence,name"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _sql_constraints = [("is_other_uniq", "unique(is_other)", "Other location must be unique")]

    active = fields.Boolean(default=True, tracking=True)
    sequence = fields.Integer(
        string="Sequence",
        default=10
    )
    name = fields.Char(string="Location", tracking=True, translate=True)
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        tracking=True,
        required=True,
        domain="[('has_locations', '=', True)]",
        ondelete="cascade"
    )
    is_other = fields.Boolean(string="Other", tracking=True)

