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
            'document_types': request.env['document.file.type'].sudo().search(domain),
            'areas': request.env['helpdesk.ticket.area'].sudo().search(domain),
            'submission_token': submission_token
        }
        return request.render("quality_control_bol.document_form", data)

