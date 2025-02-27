# -*- coding: utf-8 -*-
import base64
import logging
import uuid

from datetime import datetime
from odoo import http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

headers = {"content-type": "application/json;charset=utf-8"}
#
# # Example of generating the link
# timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
# link = f"/change_stage/{ticket_id}/{action}?timestamp={timestamp}"


class HelpdeskTicketController(http.Controller):

    @http.route("/gss", auth="user", type="http", website=True)
    def create_new_ticket_gss(self, **kw):
        """ Renders the help desk ticket creation form with
            necessary data such as user information,
            ticket types, categories, areas, and locations
            Args:**kw: Arbitrary keyword arguments.
            Returns:werkzeug.wrappers.Response: The rendered HTML page for the ticket form.
        """
        submission_token = str(uuid.uuid4())
        request.session['submission_token'] = submission_token

        data = {
            'user': request.env.user,
            'types': request.env['helpdesk.ticket.type'].sudo().search([]),
            'categories': request.env['helpdesk.ticket.category'].sudo().search([]),
            'default_area_id': request.env['helpdesk.ticket.area'].sudo().search([('show_in_external_portal', '=', True)], limit=1),
            'locations': request.env['helpdesk.ticket.location'].sudo().search([]),
            'submission_token': submission_token
        }
        return request.render("helpdesk_bol.gss_ticket_form", data)

    @http.route("/help_desk", auth="user", type="http", website=True)
    def create_new_ticket(self, **kw):
        """ Renders the help desk ticket creation form with
            necessary data such as user information,
            ticket types, categories, areas, and locations
            Args:**kw: Arbitrary keyword arguments.
            Returns:werkzeug.wrappers.Response: The rendered HTML page for the ticket form.
        """
        submission_token = str(uuid.uuid4())
        request.session['submission_token'] = submission_token

        data = {
            'user': request.env.user,
            'types': request.env['helpdesk.ticket.type'].sudo().search([]),
            'categories': request.env['helpdesk.ticket.category'].sudo().search([]),
            'areas': request.env['helpdesk.ticket.area'].sudo().search([('show_in_external_portal', '=', False)]),
            'locations': request.env['helpdesk.ticket.location'].sudo().search([]),
            'submission_token': submission_token
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

        # Verify CSRF token and submission token
        submission_token = kw.get('submission_token')
        print(submission_token)

        if not submission_token or submission_token != request.session.pop('submission_token', None):
            return request.render("helpdesk_bol.ticket_register", {'error_message': _('Invalid or duplicate submission.')})

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

        # Clear the session flag after processing the form
        request.session['form_submitted'] = False
        return request.render("helpdesk_bol.ticket_register", {'number': helpdesk_ticket.number})

    @http.route("/help_desk_reopen", auth="user", website=True)
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
        #
        # # Validate the timestamp
        # if not timestamp or not self._is_link_valid(timestamp):
        #     return request.render("helpdesk_bol.link_expired")

        ticket = request.env["helpdesk.ticket"].sudo().browse(int(ticket_id))
        if int(action) == 1:
            ticket.sudo().write({'stage_id': request.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_done').id})
        return request.render(
            "helpdesk_bol.reopen_close_ticket_form",{
                'id': int(ticket_id), 'name': ticket.name,
                'number': ticket.number, 'action': action, 'id': int(ticket_id)})
    #
    # def _is_link_valid(self, timestamp):
    #     """ Check if the link is within the 48-hour validity period """
    #     link_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    #     current_time = datetime.utcnow()
    #     return current_time <= link_time + timedelta(hours=48)
