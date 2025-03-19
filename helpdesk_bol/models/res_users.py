# -*- coding: utf-8 -*-
import random
import requests

from odoo import api, fields, models, registry, SUPERUSER_ID


class ResUsers(models.Model):
    _name = "res.users"
    _inherit = ["res.users", "mail.thread", "mail.activity.mixin"]

    area = fields.Char(
        string="Area Active Directory",
        help="Area Active Directory",
        tracking=True
    )
    area_ids = fields.Many2many(
        "helpdesk.ticket.area",
        string="Access Areas",
        compute="_compute_area_ids"
    )

    def _compute_area_ids(self):
        for user in self:
            area_ids = self.env['helpdesk.ticket.team'].search([('user_ids', 'in', user.id)]).mapped('area_id')
            user.area_ids = [(6, 0, area_ids.ids)]

    def _get_members_ws(self):
        url = self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.ws_url')
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    "ctlp",
                    13621,
                    "QboW7nm7qW3mZXPGpozEL3Z",
                    "res.partner",
                    "search_read",
                    [[["socio_code", "!=", False]]],
                    {"fields": ["name", "phone", "email", "socio_code", "ci",
                                "street", "street2", "city", "state_id", "country_id", "zip"]},
                ]
            },
            "id": random.randint(0, 1000000000)
        }
        response = requests.post(url, json=payload, verify=False)
        result = response.json().get('result')
        if result:
            for member in result:
                member_id = self.env['res.partner'].search([('member_code', '=', member['socio_code'])])
                if not member_id:
                    member_id = self.env['res.partner'].create({
                        'name': member['name'],
                        'phone': member['phone'],
                        'email': member['email'],
                        'member_code': member['socio_code'],
                        'ci': member['ci'],
                        'street': member['street'],
                        'street2': member['street2']})

    def _update_members_payment_ws(self):
        url = self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.ws_url')
        partner_ids = self.env['res.partner'].search([('member_code', '!=', False)])
        for partner in partner_ids:
            payload_2 = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        "ctlp",
                        13621,
                        "QboW7nm7qW3mZXPGpozEL3Z",
                        "ctlp.lista.negra",
                        "search_read",
                        [[["socio_code", "=", partner.member_code]]],
                        {"fields": ["name", "socio_code"]}
                    ]
                },
                "id": random.randint(0, 1000000000),
            }
            response2 = requests.post(url, json=payload_2, verify=False)
            result2 = response2.json().get('result')
            if result2:
                partner.payment_on_day = False
