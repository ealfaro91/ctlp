# -*- coding: utf-8 -*-

from werkzeug import utils
from logging import getLogger
from odoo import fields, http
from odoo.http import request
from odoo.addons.web.controllers import (home, session)
_logger = getLogger(__name__)


class Home(home.Home):

    @http.route('/web/login', type='http', auth='public')
    def web_login(self, login=None, redirect=None, **kw):
        user = False
        sessions = False
        terminate_past_session = False
        recommend_password_update = False
        if login:
            user = request.env['res.users'].sudo().search([('login','=',login)])

        if user and user.is_member:
            get_param = request.env['ir.config_parameter'].sudo().get_param
            is_admin = user._is_admin()

            password_lifetime = int(get_param('helpdesk_bol.password_lifetime'))
            reset_password_redirect = get_param('helpdesk_bol.forced_password_change') == 'True'
            login_ids = request.env['res.users.log'].sudo().search([('create_uid','=', user.id)])

            if user.state == 'new':
                #password_lifetime = fields.date_utils.relativedelta(days=password_lifetime)
				#last_password_reset = user.partner_id.last_password_reset or user.partner_id.create_date
				# is_password_too_old = last_password_reset + password_lifetime < fields.datetime.utcnow()
				# if is_password_too_old:
				# 	if not reset_password_redirect or is_admin:
				# 		recommend_password_update = True
				# 	else:
                request.params['login_success'] = False
                return utils.redirect('/web/reset_password?', 303)

        res = super().web_login(login=login, redirect=redirect, **kw)
        if user and user.is_member:
            if request.httprequest.method == 'POST' and not redirect:
                # Redirect only after successful login
                if request.session.uid:
                    # Redirect to your desired URL
                    return utils.redirect('/help_desk', 200)
        return res
