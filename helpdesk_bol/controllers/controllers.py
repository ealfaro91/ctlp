# -*- coding: utf-8 -*-
import base64
from datetime import datetime
import json
import logging

from odoo import http
from odoo.http import request, Response
from odoo.http import Response

from operator import itemgetter
from odoo.tools.translate import _
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers.portal import pager as portal_pager, \
    CustomerPortal
from odoo.osv.expression import OR

_logger = logging.getLogger(__name__)

headers = {"content-type": "application/json;charset=utf-8"}


class ServiceDesk(http.Controller):

    @http.route("/help_desk", auth="user", type="http", website=True)
    def index(self, **kw):
        data = {}
        types = request.env['helpdesk.ticket.type'].sudo().search([])
        categories = request.env['helpdesk.ticket.category'].sudo().search([])
        data.update({
            'user': request.env.user,
            'types': types,
            'categories': categories,
        })
        return request.render("helpdesk_bol.ticket_form", data)

    @http.route("/help_desk_close", type='http', auth="public",  methods=['POST'],
                website=True)
    def help_desk_close(self, **kw):
        helpdesk_ticket = request.env['helpdesk.ticket'].sudo().create({
            'partner_name': kw.get('name'),
            'partner_id': request.env.user.partner_id.id,
            'partner_email': request.env.user.login,
            'area': request.env.user.area,
            'name': kw.get('title'),
            'description': kw.get('description'),
            'type_id': kw.get('type_id'),
            'category_id': kw.get('category_id'),
        })
        attachment = kw.get('attachments')
        attached_file = attachment.read()
        file_base64 = base64.b64encode(attached_file)
        request.env["ir.attachment"].sudo().create({
            "name": attachment.filename,
            "res_model": helpdesk_ticket._name,
            "res_id": helpdesk_ticket.id,
            "type": "binary",
            "datas": file_base64,
        })
        return request.render("helpdesk_bol.ticket_thank_you", {})
    
    @http.route("/help_desk_reopen", type='http', auth="public",  methods=['POST'], website=True)
    def help_desk_reopen(self, **kw):
        print(kw)
        request.env["helpdesk.ticket"].sudo().search(
                [("id", "=", kw.get('id'))]).write(
                    {'reopen_reason': kw.get('reopen_reason'), 'stage_id': 2})
        return request.render("helpdesk_bol.ticket_thank_you", {})

    @http.route(
        "/change_stage/<record_id>/<action>", auth="public", website=True
    )
    def change_stage(self, record_id=None, action=None):
        """ permite al cliente que recibe el correo cambiar el estado de ticker
            para apertura o cierre definitivo
        """
        if int(action) == 1:
            request.env["helpdesk.ticket"].sudo().search(
                [("id", "=", record_id)]).write({'stage_id': 4})
        elif int(action) == 2:
            print(record_id)
            return request.render("helpdesk_bol.reopen_ticket_form", {'id' : record_id})

