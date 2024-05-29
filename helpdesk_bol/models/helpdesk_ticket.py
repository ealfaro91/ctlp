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
    max_attention_time = fields.Integer(related="subcategory_id.max_attention_time")
    elapsed_attention_time = fields.Integer(compute="_compute_attention_time_state")
    attention_time_state = fields.Selection([
        ("on_time", "On time"), ("delayed", "Delayed"), ("on_hold", "On hold")],
        default="on_time", string="Attention time state",
        compute="_compute_attention_time_state"
    )
    resolution = fields.Text(string="Resolution")
    area = fields.Char(string="Area")
    area_id = fields.Many2one(
        "helpdesk.ticket.area", string="Area",
       # default=lambda self: self.env.ref('helpdesk_bol.helpdesk_ticket_area_ti')
    )
    user_id = fields.Many2one(related="subcategory_id.user_id")

    @api.onchange()

    # @api.model
    # def create(self, vals):
    #     res = super(HelpdeskTicket, self).create(vals)
    #     template = self.env.ref('helpdesk_bol.ticket_creation')
    #     if template:
    #         template.send_mail(res.id, force_send=False)
    #
    #     return res

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
