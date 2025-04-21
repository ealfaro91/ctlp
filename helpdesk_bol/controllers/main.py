# -*- coding: utf-8 -*-

import werkzeug

from werkzeug import utils
from logging import getLogger
import odoo
from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import UserError

from werkzeug.urls import url_encode


from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url, is_user_internal


# Shared parameters for all login/signup flows
SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'city', 'country_id', 'lang', 'signup_email'}
LOGIN_SUCCESSFUL_PARAMS = set()


from odoo.addons.web.controllers import (home, session)
_logger = getLogger(__name__)


class Home(home.Home):

    # @http.route('/web/login', type='http', auth='public')
    # def web_login(self, login=None, redirect=None, **kw):
    #     user = False
    #     sessions = False
    #     terminate_past_session = False
    #     recommend_password_update = False
    #     if login:
    #         user = request.env['res.users'].sudo().search([('login', '=', login)])
    #
    #     if user and user.is_member:
        #    return utils.redirect('/web/socios/login')
            # get_param = request.env['ir.config_parameter'].sudo().get_param
            # is_admin = user._is_admin()
            #
            # password_lifetime = int(get_param('helpdesk_bol.password_lifetime'))
            # reset_password_redirect = get_param('helpdesk_bol.forced_password_change') == 'True'
            # login_ids = request.env['res.users.log'].sudo().search([('create_uid','=', user.id)])
            #
            # if user.state == 'new':
            #     #password_lifetime = fields.date_utils.relativedelta(days=password_lifetime)
			# 	#last_password_reset = user.partner_id.last_password_reset or user.partner_id.create_date
			# 	# is_password_too_old = last_password_reset + password_lifetime < fields.datetime.utcnow()
			# 	# if is_password_too_old:
			# 	# 	if not reset_password_redirect or is_admin:
			# 	# 		recommend_password_update = True
			# 	# 	else:
            #     request.params['login_success'] = False
            #     return utils.redirect('/web/reset_password?', 303)


        #return res

    def _login_redirect(self, uid, redirect=None):
        if not redirect and not is_user_internal(uid):
            redirect = '/my/account'
        return super()._login_redirect(uid, redirect=redirect)

    @http.route('/web/socios/login', type='http', auth='public', website=True)
    def web_members_login(self, login=None, redirect=None, **kw):
        values = {
            'website': request.website,
            'page_name': 'socios_login',
        }
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
           # return request.redirect(redirect)
            return request.render('helpdesk_bol.login_socios', values)
        if request.httprequest.method == 'POST':
            user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
            _logger.info("Logging in: %s", user.login)

            # Validate if user exists and is a portal user
            if not user or user.has_group('base.group_user'):  # group_user = internal user
                return request.render('helpdesk_bol.login_socios', {
                    'error': _("ID card not found"),
                })
             # Manually authenticate the user
            _logger.info("Logging in: %s", user.password)
            request.session.authenticate(request.db, login, login)  # password ignored here
            return request.redirect('/help_desk')

        return request.render('helpdesk_bol.login_socios', values)

        # ensure_db()
        # request.params['login_success'] = False
        # if request.httprequest.method == 'GET' and redirect and request.session.uid:
        #     return request.redirect(redirect)
        #
        # # simulate hybrid auth=user/auth=public, despite using auth=none to be able
        # # to redirect users when no db is selected - cfr ensure_db()
        # if request.env.uid is None:
        #     if request.session.uid is None:
        #         # no user -> auth=public with specific website public user
        #         request.env["ir.http"]._auth_method_public()
        #     else:
        #         # auth=user
        #         request.update_env(user=request.session.uid)
        #
        # values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        # try:
        #     values['databases'] = http.db_list()
        # except odoo.exceptions.AccessDenied:
        #     values['databases'] = None
        #
        # if request.httprequest.method == 'POST':
        #     try:
        #         uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
        #         request.params['login_success'] = True
        #         return request.redirect(self._login_redirect(uid, redirect=redirect))
        #     except odoo.exceptions.AccessDenied as e:
        #         if e.args == odoo.exceptions.AccessDenied().args:
        #             values['error'] = _("Wrong login/password")
        #         else:
        #             values['error'] = e.args[0]
        # else:
        #     if 'error' in request.params and request.params.get('error') == 'access':
        #         values['error'] = _('Only employees can access this database. Please contact the administrator.')
        #
        # if 'login' not in values and request.session.get('auth_login'):
        #     values['login'] = request.session.get('auth_login')
        #
        # if not odoo.tools.config['list_db']:
        #     values['disable_database_manager'] = True
        #
        # response = request.render('helpdesk_bol.login_socios', values)
        # response.headers['Cache-Control'] = 'no-cache'
        # response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        # if login:
        #     user = request.env['res.users'].sudo().search([('login', '=', login)])
        #     if user and user.is_member:
        #         if request.httprequest.method == 'POST' and not redirect:
        #             # Redirect only after successful login
        #             if request.session.uid:
        #                 # Redirect to your desired URL
        #                 return utils.redirect('/help_desk')
        #
        # res = super().web_login(login=login, redirect=redirect, **kw)
       # return response

    # @http.route('/socios/authenticate', type='http', auth='public', website=True, csrf=False)
    # def socios_authenticate(self, **post):
    #     login = post.get('login')
    #     user = request.env['res.users'].sudo().search([
    #         ('login', '=', login),
    #         ('groups_id', 'in', request.env.ref('base.group_portal').id)
    #     ], limit=1)
    #
    #     if user:
    #         request.session.uid = user.id
    #         return redirect('/my')  # or any portal page
    #
    #     return request.render('your_module.simple_portal_login_template', {
    #         'error': 'Invalid login. Please try again.'
    #     })
    #
    #
    #
