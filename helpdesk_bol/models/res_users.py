# -*- coding: utf-8 -*-
import requests

from odoo import api, fields, models, registry, SUPERUSER_ID
from odoo.exceptions import AccessDenied


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

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        try:
            return super(ResUsers, cls)._login(db, login, password, user_agent_env=user_agent_env)
        except AccessDenied as e:
            with registry(db).cursor() as cr:
                cr.execute("SELECT id FROM res_users WHERE lower(login)=%s", (login,))
                res = cr.fetchone()
                if res:
                    raise e

                env = api.Environment(cr, SUPERUSER_ID, {})
                Ldap = env['res.company.ldap']
                for conf in Ldap._get_ldap_dicts():
                    entry = Ldap._authenticate(conf, login, password)
                    if entry:
                        return Ldap._get_or_create_user(conf, login, entry)
                    else:
                        if env['ir.config_parameter'].sudo().get_param('helpdesk_bol.login_from_ws'):
                            url = env['ir.config_parameter'].sudo().get_param('helpdesk_bol.ws_url')
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
                                    [[["ci", "=", "3371503"]]],
                                    {"fields": ["name", "phone", "email", "socio_code", "ci"]}
                                ]
                            },
                            "id": 10475
                        }
                        response = requests.post(url, json=payload, verify=False)
                raise e


