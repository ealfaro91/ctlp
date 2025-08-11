# -*- coding: utf-8 -*-

import binascii
from odoo import http, fields, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

from odoo.exceptions import AccessError, MissingError
from odoo.http import request

import base64

class PdfInlineController(http.Controller):
    @http.route('/pdf_inline/<model>/<int:record_id>/<field>', type='http', auth='user')
    def pdf_inline(self, model, record_id, field):
        record = request.env[model].sudo().browse(record_id)
        pdf_data = getattr(record, field)
        if not pdf_data:
            return request.not_found()
        pdf_bytes = base64.b64decode(pdf_data)
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', 'inline; filename="document.pdf"'),
        ]
        return request.make_response(pdf_bytes, headers)
