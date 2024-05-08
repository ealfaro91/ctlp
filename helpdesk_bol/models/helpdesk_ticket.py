# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    category_id = fields.Many2one(
        comodel_name="helpdesk.ticket.category",
        string="Category",
        domain="[('type_id', '=', type_id)]"
    )
    subcategory_id = fields.Many2one(
        "helpdesk.ticket.subcategory",
        string="Subcategory",
        domain="[('category_id', '=', category_id)]"
    )
    max_attention_time = fields.Integer(related="category_id.max_attention_time")
    elapsed_attention_time = fields.Integer(compute="_compute_attention_time_state")
    attention_time_state = fields.Selection([
        ("delayed", "Delayed"), ("on_time", "On time")],
        default="on_time", string="Attention time state",
        compute="_compute_attention_time_state"
    )
    resolution = fields.Text(string="Resolution")
    area = fields.Char(string="Area")
    #user_id = fields.Many2one(related="category_id.user_id")

    def _compute_attention_time_state(self):
        for ticket in self:
            ticket.attention_time_state = "on_time"

            today = fields.Datetime.today()
            format = "%H:%M:%S"

            if not ticket.closed_date:
                ticket.elapsed_attention_time = 0#datetime.strptime(today, format) - (ticket.create_date, format)
            else:
                ticket.elapsed_attention_time = 0#datetime.strptime(ticket.closed_date, format) - (ticket.create_date, format)

        # horas desde create_date hasta cambio a cerrado or resolution_date
