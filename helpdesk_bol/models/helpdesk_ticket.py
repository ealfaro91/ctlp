# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    category_id = fields.Many2one(
        comodel_name="helpdesk.ticket.category",
        string="Category",
        domain="[('type_id', '=', type_id)]",
        tracking=True
    )
    subcategory_id = fields.Many2one(
        "helpdesk.ticket.subcategory",
        string="Subcategory",
        domain="[('category_id', '=', category_id)]",
        tracking=True
    )
    max_attention_time = fields.Integer(related="subcategory_id.max_attention_time")
    elapsed_attention_time = fields.Integer(string="Elapsed Attention Time (hours)", compute="_compute_attention_time_state")
    attention_time_state = fields.Selection([
        ("on_time", "On time"), ("delayed", "Delayed"), ("on_hold", "On hold")],
        default="on_time", string="Attention time state",
        compute="_compute_attention_time_state"
    )
    resolution = fields.Text(string="Resolution", tracking=True)
    reopen_reason = fields.Text(string="Reopen reason", tracking=True)
    area = fields.Char(string="Area", tracking=True)
    area_id = fields.Many2one(
        "helpdesk.ticket.area", string="Area", tracking=True
       # default=lambda self: self.env.ref('helpdesk_bol.helpdesk_ticket_area_ti')
    )
    user_id = fields.Many2one(related="category_id.user_id", tracking=True)


    @api.model
    def create(self, vals):
        res = super(HelpdeskTicket, self).create(vals)
        res.team_id = self.env['helpdesk.ticket.team'].search([('area_type', '=', 'TI')]).id
        template = self.env.ref('helpdesk_bol.ticket_creation')
        if template:
            template.send_mail(res.id, force_send=False)
        return res

    def _compute_attention_time_state(self):
        """ Compute attention time """
        for ticket in self:
            ticket.attention_time_state = "on_time"
            if ticket.stage_id.id == self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_awaiting').id:
                ticket.attention_time_state = "on_hold"
            today = fields.Datetime.now()
            format = "%Y-%m-%d %H:%M:%S"
            date = fields.Datetime.to_string(ticket.closed_date or today)
            ticket.elapsed_attention_time = ((datetime.strptime(date, format) - datetime.strptime(fields.Datetime.to_string(ticket.create_date), format)).seconds / 3600)
            if  ticket.elapsed_attention_time > ticket.max_attention_time:
                    ticket.attention_time_state = "delayed"