# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class CompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    def _map_ldap_attributes(self, conf, login, ldap_entry):
        """
        Compose values for a new resource of model res_users,
        based upon the retrieved ldap entry and the LDAP settings.
        :param dict conf: LDAP configuration
        :param login: the new user's login
        :param tuple ldap_entry: single LDAP result (dn, attrs)
        :return: parameters for a new resource of model res_users
        :rtype: dict
        """
        ldap_dict = {
            'name': tools.ustr(ldap_entry[1]['cn'][0]),
            'login': login,
            'company_id': conf['company'][0],

        }
        if not ldap_entry[1]['department'] or not ldap_entry[1]['mail']:
            raise ValidationError("The department or mail is not configured for the user. Please adjust it")
        else:
            ldap_dict['area'] = tools.ustr(ldap_entry[1]['department'][0])
            ldap_dict['email'] = tools.ustr(ldap_entry[1]['mail'][0])
        return ldap_dict

    def _get_or_create_user(self, conf, login, ldap_entry):
        """
        Retrieve an active resource of model res_users with the specified
        login. Create the user if it is not initially found.

        :param dict conf: LDAP configuration
        :param login: the user's login
        :param tuple ldap_entry: single LDAP result (dn, attrs)
        :return: res_users id
        :rtype: int
        """
        login = tools.ustr(login.lower().strip())
        self.env.cr.execute("SELECT id, active FROM res_users WHERE lower(login)=%s", (login,))
        res = self.env.cr.fetchone()
        if res:
            if res[1]:
                return res[0]
        elif conf['create_user']:
            _logger.debug("Creating new Odoo user \"%s\" from LDAP" % login)
            values = self._map_ldap_attributes(conf, login, ldap_entry)
            SudoUser = self.env['res.users'].sudo().with_context(no_reset_password=True)
            if conf['user']:
                values['active'] = True
                return SudoUser.browse(conf['user'][0]).copy(default=values).id
            else:
                return SudoUser.create(values).id

        raise AccessDenied(_("No local user found for LDAP login and not configured to create one"))
