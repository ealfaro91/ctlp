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
    def create_new_ticket(self, **kw):
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
        user_id = request.env['helpdesk.ticket.category'].sudo().search([
            ('id', '=', kw.get('category_id'))]).user_id
        helpdesk_ticket = request.env['helpdesk.ticket'].sudo().create({
            'partner_name': kw.get('name'),
            'partner_id': request.env.user.partner_id.id,
            'partner_email': request.env.user.partner_id.email,
            'area': request.env.user.area,
            'name': kw.get('title'),
            'description': kw.get('description'),
            'type_id': kw.get('type_id'),
            'category_id': kw.get('category_id'),
            'user_id': user_id.id,
        })

        if kw.get('attachments'):
            attached_files = request.httprequest.files.getlist('attachments')
            for attachment in attached_files:
                attached_file = attachment.read()
                request.env['ir.attachment'].sudo().create({
                    'name': attachment.filename,
                    'res_model': helpdesk_ticket._name,
                    'res_id': helpdesk_ticket.id,
                    'type': 'binary',
                    'datas': base64.b64encode(attached_file),
                })
        return request.render("helpdesk_bol.ticket_thank_you", {'number': helpdesk_ticket.number})

    @http.route("/help_desk_reopen", type='http', auth="public",  methods=['POST'], website=True)
    def help_desk_reopen(self, **kw):
        print(kw)
        request.env["helpdesk.ticket"].sudo().search(
                [("id", "=", kw.get('id'))]).write(
                    {'reopen_reason': kw.get('reopen_reason'), 'stage_id': 2})
        return request.render("helpdesk_bol.ticket_thank_you", {})

    @http.route(
        "/change_stage/<int:ticket_id>/<action>", auth="public", website=True
    )
    def change_stage(self, ticket_id=None, action=None):
        """ permite al cliente que recibe el correo cambiar el estado de ticker
            para apertura o cierre definitivo
        """
        ticket = request.env["helpdesk.ticket"].sudo().browse(int(ticket_id))
        if int(action) == 1:
            ticket.write({'stage_id': request.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_done').id})
            return request.render("helpdesk_bol.close_ticket_form",
                                  {'name': ticket.name, 'number': ticket.number})
        elif int(action) == 2:
            return request.render("helpdesk_bol.reopen_ticket_form",
                                  {'id': int(ticket_id), 'name': ticket.name, 'number': ticket.number})

