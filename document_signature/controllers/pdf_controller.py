# -*- coding: utf-8 -*-

import base64

from odoo import http, fields, _
from odoo.http import request


class PdfInlineController(http.Controller):
    """Controller to handle inline PDF display in Odoo."""

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
