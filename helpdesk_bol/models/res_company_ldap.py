# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models, tools


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
            'company_id': conf['company'][0]
        }
        if ldap_entry[1].get(['department']):
            ldap_dict['area'] = tools.ustr(ldap_entry[1]['department'][0]),

        return ldap_dict
