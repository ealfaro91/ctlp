# -*- coding: utf-8 -*-
import base64

import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

headers = {"content-type": "application/json;charset=utf-8"}


class HelpdeskTicketController(http.Controller):

    @http.route("/help_desk", auth="user", type="http", website=True)
    def create_new_ticket(self, **kw):
        """ Renders the help desk ticket creation form with
            necessary data such as user information,
            ticket types, categories, areas, and locations
            Args:**kw: Arbitrary keyword arguments.
            Returns:werkzeug.wrappers.Response: The rendered HTML page for the ticket form.
        """

        data = {
            'user': request.env.user,
            'types': request.env['helpdesk.ticket.type'].sudo().search([]),
            'categories': request.env['helpdesk.ticket.category'].sudo().search([]),
            'areas': request.env['helpdesk.ticket.area'].sudo().search([]),
            'locations': request.env['helpdesk.ticket.location'].sudo().search([]),
            'csrf_token': http.Request.csrf_token(request),
        }
        return request.render("helpdesk_bol.ticket_form", data)

    @http.route("/help_desk_close", type='http', auth="user",  methods=['POST'],
                website=True)
    def help_desk_close(self, **kw):
        """ Handles the closing of a help desk ticket.
           This method is an HTTP route that processes the form submission for closing
           a help desk ticket. It creates a new help desk ticket record with the provided
           details and attaches any uploaded files to the ticket.
           Args: **kw: Arbitrary keyword arguments containing the form data.
           Returns: werkzeug.wrappers.Response: The rendered HTML page for the thank you message.
           """
        session_token = http.Request.csrf_token(request)
        form_token = kw.get('csrf_token')

        _logger.info("%s %s" % (session_token, form_token))

        # if not session_token or session_token != form_token:
        #     return request.render("helpdesk_bol.ticket_register", {'error_message': 'Invalid or expired form token.'})

        helpdesk_ticket = request.env['helpdesk.ticket'].sudo().create({
            'partner_id': request.env.user.partner_id.id,
            'partner_email': request.env.user.partner_id.email,
            'area': request.env.user.area,
            'name': kw.get('title'),
            'description': kw.get('description'),
            'area_id': kw.get('area_id'),
            'team_id': request.env['helpdesk.ticket.team'].sudo().search([
                ('area_id', '=', int(kw.get('area_id')))], limit=1).id,
            'type_id': kw.get('type_id'),
            'category_id': kw.get('category_id'),
            'location_id': kw.get('location_id'),
            'user_id': request.env['helpdesk.ticket.category'].sudo().browse(int(kw.get('category_id'))).user_id.id,
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
        return request.render("helpdesk_bol.ticket_register", {'number': helpdesk_ticket.number})

    @http.route("/help_desk_reopen", type='http', auth="user",  methods=['POST'], website=True)
    def help_desk_reopen(self, **kw):
        request.env["helpdesk.ticket"].sudo().browse(int(kw.get('id'))).write(
                    {'reopen_reason': kw.get('reopen_reason'), 'stage_id': 2})
        return request.render("helpdesk_bol.ticket_register", {'hide_number': True})

    @http.route(
        "/change_stage/<int:ticket_id>/<action>", auth="user", website=True
    )
    def change_stage(self, ticket_id=None, action=None):
        """ permite al cliente que recibe el correo cambiar el estado de ticker
            para apertura o cierre definitivo
        """
        ticket = request.env["helpdesk.ticket"].sudo().browse(int(ticket_id))
        if int(action) == 1:
            ticket.sudo().write({'stage_id': request.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_done').id})
            return request.render("helpdesk_bol.close_ticket_form",
                                  {'name': ticket.name, 'number': ticket.number})
        elif int(action) == 2:
            return request.render("helpdesk_bol.reopen_ticket_form",
                                  {'id': int(ticket_id), 'name': ticket.name, 'number': ticket.number})

