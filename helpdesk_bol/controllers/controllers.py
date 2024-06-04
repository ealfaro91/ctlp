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
    def service_desk_close(self, **kw):
        print(kw)
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
            request.env["helpdesk.ticket"].sudo().search(
                [("id", "=", record_id)]).write({'stage_id': 2})
        return request.redirect("/service_desk")

        #   'type_id': kw.get('type_id'),
          #   'category_id': kw.get('category_id'),
          #   'subcategory_id': kw.get('subcategory_id'),
          # #  'user_id': ,
          #   'description': kw.get('topic'),
       # })
    #     attachment = kw.get('attachments')
    #     attached_file = attachment.read()
    #     file_base64 = base64.b64encode(attached_file)
    #     request.env["ir.attachment"].sudo().create({
    #         "name": attachment.filename,
    #         "res_model": helpdesk_ticket._name,
    #         "res_id": helpdesk_ticket.id,
    #         "type": "binary",
    #         "datas": file_base64,
    #     })

        # tema_data = {
        #     'tema': kw.get('tema'),
        #     'expositor_id': kw.get('expositor_id'),
        #     'tiempo_intervencion': float(kw.get('tiempo_intervencion')),
        #     'adjunto': base64.b64encode(attachment),
        #     'sector_id': kw.get('sector_id'),
        # }
        # if kw.get('proyecto_emblematico_relacionado') == 'on':
        #     tema_data.update({'proyecto_emblematico_relacionado': True, })
        # else:
        #     tema_data.update({'proyecto_emblematico_relacionado': False, })
        # kw.update({
        #     'tema_ids': [(0, 0, tema_data)],
        # })
        # kw.update({'es_externa': True,
        #            'duracion': float(kw.get('tiempo_intervencion'))})
    #     ficha = request.env['buen.gobierno.ficha'].sudo().create(kw)
    #     kw.update({
    #         'ficha_id': ficha.id,
    #     })
    #
    # @staticmethod
    # def create_attachments(attachment, helpdesk_ticket):


