# -*- coding: utf-8 -*-
import contextlib
import logging
import random
import requests
import time


from odoo import api, fields, models, registry, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError, AccessDenied
from odoo.addons.auth_signup.models.res_partner import SignupError, now

_logger = logging.getLogger(__name__)

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
    is_member = fields.Boolean(string="Is Member", tracking=True)
    member_code = fields.Char(
        string="Member Code",
        help="Member code from Odoo v13",
        tracking=True
    )
    payment_status = fields.Selection(
        selection=[('unpaid', 'Unpaid'), ('paid', 'Paid')],
        string="Payment Status",
        help="Payment status from Odoo v13",
        tracking=True
    )

    @api.model
    def create(self, vals):
        user = super().create(vals)
        if user.partner_id:
            user.partner_id.is_member = user.is_member
            user.partner_id.member_code = user.member_code
            user.partner_id.payment_status = user.payment_status
        return user

    def write(self, vals):
        res = super().write(vals)
        for user in self:
            if 'member_code' or 'is_member' or 'payment_status' in vals and user.partner_id:
                user.partner_id.member_code = vals['member_code']
                user.partner_id.is_member = vals['is_member']
                user.partner_id.payment_status = vals['payment_status']
        return res

    def _compute_area_ids(self):
        for user in self:
            area_ids = self.env['helpdesk.ticket.team'].search([('user_ids', 'in', user.id)]).mapped('area_id')
            user.area_ids = [(6, 0, area_ids.ids)]

    def _get_members_ws(self):
        """ Get the members from the web service and create them in the system."""
        _logger.info('Getting members from the web service')
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
                    {"fields": ["name", "phone", "mobile", "email", "socio_code", "ci",
                                "street", "street2", "city", "state_id", "country_id", "zip"]},
                ]
            },
            "id": random.randint(0, 1000000000)
        }
        response = requests.post(url, json=payload, verify=False)
        result = response.json().get('result')
        if result:
            batch_size = 100
            for i in range(0, len(result), batch_size):
                batch = result[i:i + batch_size]
                _logger.info("Processing batch %s to %s", i + 1, i + len(batch))
                for member in batch:
                    user_id = self.env['res.users'].search(['|', ('login', '=', member.get('ci')), ('member_code', '=', member.get('socio_code'))])
                    if not user_id and member.get('ci'):
                        _logger.info('Creating user: %s', member.get('name'))
                        country_id = member.get('country_id')
                        state_id = member.get('state_id')
                        try :
                            user_id = self.env['res.users'].create({
                                'name': member.get('name'),
                                'login': member.get('ci'),
                                'password': member.get('ci'),
                                'phone': member.get('phone'),
                                'mobile': member.get('mobile'),
                                'email': member.get('email'),
                                'member_code': member.get('socio_code'),
                                'vat': member.get('ci'),
                                'street': member.get('street'),
                                'street2': member.get('street2'),
                                'city': member.get('city'),
                                'country_id': country_id[0] if country_id else False,
                                'state_id': state_id[0] if state_id else False,
                                'zip': member.get('zip'),
                                'is_member': True,
                                'payment_status': "paid",
                                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                            })
                            self.env.cr.commit()
                            _logger.info('User created: %s', user_id.name)
                        except Exception as commit_error:
                            _logger.error("Commit failed for user %s: %s", member.get('name'), commit_error)
            # Pausa después de cada lote
            _logger.info("Batch %s processed. Pausing before next batch...", (i // batch_size) + 1)
            time.sleep(30)  # pausa de 2 segundos (ajustable)

    def _update_members_payment_ws(self):
        """ Update the payment status of the members."""
        _logger.info('Updating payment status of the members')
        url = self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.ws_url')
        self.env.cr.execute("SELECT id, member_code FROM res_users WHERE is_member = TRUE AND member_code IS NOT NULL")
        user_rows = self.env.cr.fetchall()
        _logger.info("Found %s members to update", len(user_rows))
        member_code_map = {code: uid for uid, code in user_rows}
        member_codes = list(member_code_map.keys())

        if not member_codes:
            _logger.info("No hay códigos de miembros para consultar.")
            return

        # Hacer una sola llamada al endpoint externo con todos los códigos
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
                    "ctlp.lista.negra",
                    "search_read",
                    [[["socio_code", "in", member_codes]]],
                    {"fields": ["socio_code"]}
                ]
            },
            "id": random.randint(0, 1000000000),
        }

        response = requests.post(url, json=payload, verify=False)
        result = response.json().get('result', [])

        # Extraer los member_codes que están en la lista negra
        blacklist_codes = [r['socio_code'] for r in result if 'socio_code' in r]

        if blacklist_codes:
            user_ids_to_update = [member_code_map[code] for code in blacklist_codes if code in member_code_map]

            # Ejecutar UPDATE directo en SQL
            query = """
                    UPDATE res_users
                    SET payment_status = 'unpaid'
                    WHERE id = ANY(%s)
                """
            self.env.cr.execute(query, (user_ids_to_update,))
            _logger.info("Usuarios actualizados: %s", len(user_ids_to_update))
        else:
            _logger.info("Ningún código encontrado en lista negra.")
        # batch_size = 100
        # for i in range(0, len(user_ids), batch_size):
        #     batch = user_ids[i:i + batch_size]
        #     _logger.info("Processing batch %s to %s", i + 1, i + len(batch))
        #     for user in batch:
        #         payload_2 = {
        #             "jsonrpc": "2.0",
        #             "method": "call",
        #             "params": {
        #                 "service": "object",
        #                 "method": "execute_kw",
        #                 "args": [
        #                     "ctlp",
        #                     13621,
        #                     "QboW7nm7qW3mZXPGpozEL3Z",
        #                     "ctlp.lista.negra",
        #                     "search_read",
        #                     [[["socio_code", "=", user.member_code]]],
        #                     {"fields": ["name", "socio_code"]}
        #                 ]
        #             },
        #             "id": random.randint(0, 1000000000),
        #         }
        #         response = requests.post(url, json=payload_2, verify=False)
        #         result = response.json().get('result')
        #         if result:
        #             user.payment_status = "unpaid"
        #             self.env.cr.commit()
        #     # Pausa despues de cada lote
        #     _logger.info("Batch %s processed. Pausing before next batch...", (i // batch_size) + 1)
        #     time.sleep(30)  # pausa de 2 segundos (ajustable)

    def _action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode') or self.env.context.get('import_file'):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        account_created_template = None
        if create_mode:
            account_created_template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            if account_created_template and account_created_template._name != 'mail.template':
                _logger.error("Wrong set password template %r", account_created_template)
                return

        email_values = {
            'email_cc': False,
            'auto_delete': False,
            'message_type': 'user_notification',
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            email_values['email_to'] = user.email
            with contextlib.closing(self.env.cr.savepoint()):
                if account_created_template:
                    account_created_template.send_mail(
                        user.id, force_send=True,
                        raise_exception=True, email_values=email_values)
                else:
                    user_lang = user.lang or self.env.lang or 'en_US'
                    body = self.env['mail.render.mixin'].with_context(lang=user_lang)._render_template(
                        self.env.ref('auth_signup.reset_password_email'),
                        model='res.users', res_ids=user.ids,
                        engine='qweb_view', options={'post_process': True})[user.id]
                    context = {'lang': user_lang}  # noqa: F841
                    mail = self.env['mail.mail'].sudo().create({
                        'subject': _('Password reset'),
                        'email_from': user.company_id.email_formatted or user.email_formatted,
                        'body_html': body,
                        **email_values,
                    })
                    mail.send()
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    #
    # @classmethod
    # def _login(cls, db, login, password, user_agent_env):
    #     if not password:
    #         raise AccessDenied()
    #     ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
    #     try:
    #         with cls.pool.cursor() as cr:
    #             self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
    #             with self._assert_can_auth(user=login):
    #                 user = self.search(self._get_login_domain(login), order=self._get_login_order(), limit=1)
    #                 if not user:
    #                     raise AccessDenied()
    #                 user = user.with_user(user)
    #                 user._check_credentials(password, user_agent_env)
    #                 tz = request.httprequest.cookies.get('tz') if request else None
    #                 if tz in pytz.all_timezones and (not user.tz or not user.login_date):
    #                     # first login or missing tz -> set tz to browser tz
    #                     user.tz = tz
    #                 user._update_last_login()
    #     except AccessDenied:
    #         _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
    #         raise
    #
    #     _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)
    #
    #     return user.id
