# -*- coding: utf-8 -*-
import base64
import logging
import uuid

from odoo import http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class DocumentController(http.Controller):

    @http.route("/document_upload", auth="user", type="http", website=True)
    def create_new_document(self, **kw):
        """ Renders the help desk ticket creation form with
            necessary data such as user information,
            ticket types, categories, areas, and locations
            Args:**kw: Arbitrary keyword arguments.
            Returns:werkzeug.wrappers.Response: The rendered HTML page for the ticket form.
        """
        submission_token = str(uuid.uuid4())
        request.session['submission_token'] = submission_token
        domain = []
        data = {
            'user': request.env.user,
            'areas': request.env['helpdesk.ticket.area'].sudo().search([('show_in_directory', '=', True)]),
            'document_directories': request.env['document.directory'].sudo().search(domain),
            'submission_token': submission_token
        }
        return request.render("quality_control_bol.document_form", data)

    @http.route("/document_creation", auth="user", type="http", website=True)
    def document_creation(self, **kw):
        # Verify CSRF token and submission token
        submission_token = kw.get('submission_token')
        print(submission_token)

        if not submission_token or submission_token != request.session.pop('submission_token', None):
            return request.render("quality_control_bol.document_creation",
                                  {'error_message': _('Invalid or duplicate submission.')})


        # document = request.env['ir.attachment'].sudo().create({
        #
        #
        # })
        if kw.get('attachments'):
            ### FILTRAR AREAS CON DIRECTORIO
            document_directory = request.env['document.directory'].sudo().search(
                [('area_id', '=', int(kw.get('area_id')))], limit=1)

            attached_files = request.httprequest.files.getlist('attachments')
            for attachment in attached_files:
                attached_file = attachment.read()
                request.env['ir.attachment'].sudo().create({
                    'name': kw.get('title'),
                    'area_id': int(kw.get('area_id')),
                    'document_directory_id': document_directory.id,
               #     'document_file_type_id': int(kw.get('type')),
                    'type': 'binary',
                    'datas': base64.b64encode(attached_file),
                    'description': kw.get('description'),
                })

        # Clear the session flag after processing the form
        request.session['form_submitted'] = False
        return request.render("quality_control_bol.document_creation")
