# -*- coding: utf-8 -*-

import pytz
import logging

from datetime import datetime

from odoo import api, fields, models
from odoo.tools import datetime, DEFAULT_SERVER_DATETIME_FORMAT

TODAY = fields.Datetime.now()
_logger = logging.getLogger(__name__)


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
    max_attention_time = fields.Float(related="subcategory_id.max_attention_time")
    elapsed_attention_time = fields.Float(
        string="Elapsed Attention Time (hours)",
        compute="_compute_attention_time_state",
    )
    attention_time_state = fields.Selection([
        ("on_time", "On time"), ("delayed", "Delayed")],
        default="on_time", string="Attention time state",
        compute="_compute_attention_time_state",
        search="_search_attention_time_state"
    )
    resolution = fields.Text(string="Resolution", tracking=True)
    reopen_reason = fields.Text(string="Reopen reason", tracking=True)
    area = fields.Char(string="Area", tracking=True)
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        tracking=True,
        default=lambda self: self.env.ref('helpdesk_bol.helpdesk_ticket_area_ti')
    )
    user_id = fields.Many2one("res.users", tracking=True)
    create_date_utc = fields.Datetime(
        compute="_get_create_date_userutc"
    )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email
            self.area = self.partner_id.area

    def _search_attention_time_state(self, operator, value):
        other_record_ids = self.search([])
        delayed_ids = other_record_ids.filtered(lambda x: 0 < x.max_attention_time < (
                (datetime.strptime(fields.Datetime.to_string(x.closed_date or TODAY), DEFAULT_SERVER_DATETIME_FORMAT)
                 - datetime.strptime(fields.Datetime.to_string(x.create_date), DEFAULT_SERVER_DATETIME_FORMAT)).seconds / 3600
        ))

        if value == "delayed":
            return [('id', 'in', delayed_ids.ids)]
        elif value == "on_time":
            return [('id', 'in', (other_record_ids - delayed_ids).ids)]

    def _get_create_date_userutc(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        for ticket in self:
            ticket.create_date_utc = datetime.strftime(pytz.utc.localize(
                datetime.strptime(fields.Datetime.to_string(ticket.create_date),
                                  DEFAULT_SERVER_DATETIME_FORMAT)
            ).astimezone(local), "%Y-%m-%d %H:%M:%S")

    @api.onchange("category_id")
    def _onchange_user_id(self):
        for ticket in self:
            if ticket.category_id.user_id:
                ticket.user_id = ticket.category_id.user_id.id

    @api.model
    def create(self, vals):
        res = super(HelpdeskTicket, self).create(vals)
        res.team_id = self.env['helpdesk.ticket.team'].search([('area_type', '=', 'TI')]).id
        template = self.env.ref('helpdesk_bol.ticket_creation')
        if template:
            template.send_mail(res.id, force_send=False)
        return res

    def _compute_attention_time_state(self):
        """ Compute attention time
        - If ticket is in waiting time is stopped
        - If ticket is closed elapsed_time
        Time on waiting is not counted, so it must count first time closed and time
        """
        for ticket in self:
            ticket.attention_time_state = "on_time"
            ticket.elapsed_attention_time = ticket.elapsed_attention_time or 0
            waiting = [self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_awaiting').id,
                       self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_onpause').id,
                       self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_done').id]
            if ticket.stage_id.id in waiting:
                continue
            else:
                date = fields.Datetime.to_string(TODAY)
                ticket.elapsed_attention_time = (
                    (datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
                     - datetime.strptime(fields.Datetime.to_string(ticket.create_date), DEFAULT_SERVER_DATETIME_FORMAT)).seconds / 3600
                )
            if ticket.elapsed_attention_time > ticket.max_attention_time > 0:
                ticket.attention_time_state = "delayed"

    @api.model
    def _automatic_closure(self):
        """
        Changes stage to closed if customer didn't
        answer in the time period settled in configurations
        """
        tickets = self.search([
            ('stage_id', '=',
             self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_awaiting').id)])
        time_to_closure = float(
            self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.time_to_close_ticket'))
        for ticket in tickets:
            time_from_update = (
                (datetime.strptime(fields.Datetime.to_string(TODAY), DEFAULT_SERVER_DATETIME_FORMAT)
                 - datetime.strptime(fields.Datetime.to_string(ticket.last_stage_update),
                                     DEFAULT_SERVER_DATETIME_FORMAT)).total_seconds() / 3600
            )
            _logger.info(ticket.number)
            _logger.info(time_from_update)
            if time_from_update >= time_to_closure:
                ticket.sudo().write({'stage_id': self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_done').id})
                _logger.info(ticket.stage_id.name)


