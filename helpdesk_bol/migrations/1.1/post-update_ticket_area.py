# -*- coding:  utf-8 -*-
import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Executing migration[%s]." % version)
    env = api.Environment(cr, SUPERUSER_ID, {})
    ticket_type_ids = env['helpdesk.ticket.type'].search([('area_id', '=', False)])
    category_ids = env['helpdesk.ticket.category'].search([('area_id', '=', False)])
    subcategory_ids = env['helpdesk.ticket.subcategory'].search([('area_id', '=', False)])

    ticket_type_ids.write({'area_id': env.ref('helpdesk_bol.helpdesk_ticket_area_ti').id})
    category_ids.write({'area_id': env.ref('helpdesk_bol.helpdesk_ticket_area_ti').id})
    subcategory_ids.write({'area_id': env.ref('helpdesk_bol.helpdesk_ticket_area_ti').id})
