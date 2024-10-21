# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HelpdeskTicketSubCategory(models.Model):
    _name = "helpdesk.ticket.subcategory"
    _description = "Helpdesk Ticket Sub-Category"
    _order = "sequence,name"
    _inherit = ["mail.thread", "mail.activity.mixin",]

    @api.onchange('area_id')
    def _onchange_area_id(self):
        self.category_id = False

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Sub-Category", required=True, tracking=True, translate=True)
    category_id = fields.Many2one(
        "helpdesk.ticket.category",
        string="Category",
        required=True,
        tracking=True,
        domain="[('area_id', '=', area_id)]"
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10
    )
    max_attention_time = fields.Float(string="Max attention time (hours)", tracking=True)
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        tracking=True,
        required=True
    )
    color = fields.Integer(
        string="Color Index", related="area_id.color",
        tracking=True, store=True
    )


