# -*- coding: utf-8 -*-

import base64
import datetime
import io
import pytz

from dateutil.relativedelta import relativedelta

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfFileReader, PdfFileWriter  # 👈 API vieja

from odoo import api, models, fields


class DocumentSignature(models.AbstractModel):
    _name = "document.signature.mixin"
    _description = "Abstract Model for Document Signature"

    def _create_log(self):
        self.approval_log_ids.create({
            'user_id': self.env.user.id,
            'signed_date': fields.Datetime.now(),
            'sign_signature': self.env.user.sign_signature,
            'approval_type': 'author',
        })



    # def button_author_sign(self):
    #     """ Calls the method to attach the signature to the PDF document. """
    #     if not self.requested_by_id.sign_signature:
    #         raise ValidationError(_("The author signature is required. Go to the user settings to add it."))
    #     new_pdf = self.attach_signature_to_pdf(self.document, self.requested_by_id.sign_signature)
    #     self.document_signed = new_pdf
    #     self.signed_by_author = True
    #     return {
    #         "type": "ir.actions.client",
    #         "tag": "display_notification",
    #         "params": {
    #             "message": _("The FSN has been signed by the author."),
    #             "next": {"type": "ir.actions.act_window_close"},
    #             "sticky": False,
    #             "type": "success",
    #         }
    #     }

    # FSN

    def button_send_approval_request(self):
        """Send approval request emails to all users in the approval log.
        returns a notification message."""

        for rec in self:
            if not rec.approval_log_ids:
                raise ValidationError(
                    _("There are no users in the approval log to send the request.")
                )
            rec.assign_signature_coords(rec.approval_log_ids)
            for user in rec.approval_log_ids.mapped("user_id"):
                mail_template = self.env.ref(
                    "project_bol.fsn_approval_request_email", raise_if_not_found=True
                )
                # Aquí estamos pasando al contexto el usuario
                mail_template.write({"email_to": user.email})
                mail_template.sudo().with_context(
                    user_name=user.name,
                ).send_mail(
                    rec.id, force_send=True, raise_exception=True
                )
            for log in rec.approval_log_ids:
                log.request_sign_date = fields.Datetime.now()
            rec.sent_approval_request = True
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "message": _("The approval request has been sent successfully."),
                    "next": {"type": "ir.actions.act_window_close"},
                    "sticky": False,
                    "type": "success",
                }
            }


    @staticmethod
    def assign_signature_coords(approval_logs, page_width=595, base_x=50, base_y=180):
        """
        Assign signature coordinates starting from an existing base signature at (base_x, base_y).
        Places 2 signatures per row, going downward.
        """
        sig_width, sig_height = 80, 35
        margin_x = 20
        margin_y = 40
        for idx, log in enumerate(approval_logs):
            # idx=0 → primera firma a la derecha de la base
            # idx=1 → segunda fila, izquierda
            # idx=2 → segunda fila, derecha, etc.
            col = (idx + 1) % 2  # sumamos 1 porque la primera ya está
            row = (idx + 1) // 2

            x = base_x + col * (sig_width + margin_x)
            y = base_y - row * (sig_height + margin_y)
            log.write({'x_coord': x, 'y_coord': y})

    @staticmethod
    def attach_signature_to_pdf(pdf_binary_base64, signature_image_base64, quadrant=1):
        """ Attach signature to the last page of the PDF."""

        if not pdf_binary_base64 or not signature_image_base64:
            return pdf_binary_base64  # Si falta algo, no modificamos
        # Decodificar los datos binarios
        pdf_data = base64.b64decode(pdf_binary_base64)
        signature_image = base64.b64decode(signature_image_base64)
        # Leer el PDF original
        original_pdf = PdfFileReader(io.BytesIO(pdf_data))
        # Buscar última página válida
        last_page = None
        last_page_index = None
        for idx in reversed(range(original_pdf.numPages)):
            page = original_pdf.getPage(idx)
            try:
                if hasattr(page, "mediaBox") and len(page.mediaBox) == 4:
                    last_page = page
                    last_page_index = idx
                    break
            except Exception:
                continue
        # Si no hay página válida, usar primera
        if last_page is None:
            last_page = original_pdf.getPage(0)
            last_page_index = 0
            width, height = 595, 842  # tamaño A4 por defecto
        else:
            try:
                width = float(last_page.mediaBox.getWidth())
                height = float(last_page.mediaBox.getHeight())
            except Exception:
                width, height = 595, 842

        quadrant_positions = {
            1: (50, 180),  # abajo izquierda (más arriba)
            2: (200, 180),  # un poco más al centro
            3: (width - 350, 180),  # centro derecha
            4: (width - 150, 180),  # abajo derecha
        }

        # Obtener coordenadas según el cuadrante
        x, y = quadrant_positions.get(quadrant, quadrant_positions[1])
        sig_width, sig_height = 80, 35
        # Crear PDF con la firma
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))
        can.setFillColor(colors.white)
        can.rect(x, y, sig_width, sig_height, fill=1, stroke=0)
        can.drawImage(ImageReader(io.BytesIO(signature_image)), x, y,
                      width=sig_width, height=sig_height, mask='auto')
        # Agregar texto debajo de la firma
        text_x = x
        text_y = y - 12  # 12 puntos debajo de la firma
        can.setFont("Helvetica", 10)
        can.setFillColor(colors.black)
        can.drawString(text_x, text_y, f"Elaborado por:")
        can.save()
        # Fusionar firma con la última página
        packet.seek(0)
        signature_pdf = PdfFileReader(packet)
        writer = PdfFileWriter()
        for i in range(original_pdf.numPages):
            page = original_pdf.getPage(i)
            if i == last_page_index:
                page.mergePage(signature_pdf.getPage(0))  # 👈 API vieja
            writer.addPage(page)
        # Guardar PDF final
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return base64.b64encode(output_stream.read())


    # ATTACHMENT

    def button_send_approval_request(self):
        """Send approval request emails to all users in the approval log."""
        for rec in self:
            if not rec.approval_log_ids:
                raise ValidationError(
                    _("There are no users in the approval log to send the request.")
                )
            rec.assign_signature_coords(rec.approval_log_ids)
            for user in rec.approval_log_ids.mapped("user_id"):
                mail_template = self.env.ref(
                    "quality_control_bol.document_approval_email", raise_if_not_found=True
                )
                # Aquí estamos pasando al contexto el usuario
                mail_template.write({"email_to": user.email})
                mail_template.sudo().with_context(
                    user_name=user.name,
                ).send_mail(
                    rec.id, force_send=True, raise_exception=True
                )
            for log in rec.approval_log_ids:
                log.request_sign_date = fields.Datetime.now()
            rec.sent_approval_request = True
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("The approval request has been sent successfully."),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'success',
                }}

    @staticmethod
    def assign_signature_coords(approval_logs, page_width=595, base_x=None, base_y=800):
        """
        Assign signature coordinates in a table at the top of the page.
        Columns: author (left), reviewer (center), approver (right).
        Multiple rows if needed.
        """
        sig_width, sig_height = 80, 35
        margin_x = 20
        margin_y = 40

        # Column X positions
        columns = {
            'author': 50,
            'reviewer': (page_width - sig_width) / 2,
            'approver': page_width - sig_width - 50,
        }

        # Counters para filas por columna
        row_counters = {'author': 0, 'reviewer': 0, 'approver': 0}

        for log in approval_logs:
            col_x = columns.get(log.approval_type, 50)  # default a author
            row = row_counters[log.approval_type]
            x = col_x
            y = base_y - row * (sig_height + margin_y)
            log.write({'x_coord': x, 'y_coord': y})
            row_counters[log.approval_type] += 1



    @staticmethod
    def attach_signature_to_pdf(pdf_binary_base64, signature, approval_logs):
        """
        Adjunta firmas en PDF A4:
        - Firma elaborador a la izquierda
        - Columnas de reviewer y approver a la derecha de la firma elaborador
        - Firmas se apilan verticalmente sin solaparse
        """
        if not pdf_binary_base64:
            return pdf_binary_base64

        pdf_data = base64.b64decode(pdf_binary_base64)
        original_pdf = PdfFileReader(io.BytesIO(pdf_data))

        # Última página válida
        last_page_index = None
        for idx in reversed(range(original_pdf.numPages)):
            page = original_pdf.getPage(idx)
            try:
                if hasattr(page, "mediaBox") and len(page.mediaBox) == 4:
                    last_page_index = idx
                    width = float(page.mediaBox.getWidth())
                    height = float(page.mediaBox.getHeight())
                    break
            except Exception:
                continue
        if last_page_index is None:
            last_page_index = 0
            width, height = 595, 842

        # Separar logs por tipo
        reviewers = [log for log in approval_logs if log.approval_type == 'reviewer']
        approvers = [log for log in approval_logs if log.approval_type == 'approver']

        # Configuración
        sig_width, sig_height = 80, 35
        margin_y = 20
        base_y = height - 100  # desde la parte superior
        base_x_elab = 50  # firma elaborador
        base_x_review = base_x_elab + sig_width + 50  # columna reviewer
        base_x_approve = base_x_review + sig_width + 50  # columna approver

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))

        # Dibujar firma elaborador
        if signature:
            sig_elab = base64.b64decode(signature)
            can.drawImage(ImageReader(io.BytesIO(sig_elab)), base_x_elab, base_y,
                          width=sig_width, height=sig_height, mask='auto')
            can.setFont("Helvetica", 10)
            can.setFillColor(colors.black)
            can.drawString(base_x_elab, base_y - 12, "Elaborado por:")

        # Función para dibujar columnas
        def draw_column(logs, base_x, label):
            for i, log in enumerate(logs):
                x = base_x
                y = base_y - i * (sig_height + margin_y)
                sig_img = base64.b64decode(log.signature_image)
                can.drawImage(ImageReader(io.BytesIO(sig_img)), x, y,
                              width=sig_width, height=sig_height, mask='auto')
                can.setFont("Helvetica", 10)
                can.setFillColor(colors.black)
                can.drawString(x, y - 12, f"{label}:")

        draw_column(reviewers, base_x_review, "Revisado por")
        draw_column(approvers, base_x_approve, "Aprobado por")

        can.save()

        # Fusionar con PDF original
        packet.seek(0)
        signature_pdf = PdfFileReader(packet)
        writer = PdfFileWriter()
        for i in range(original_pdf.numPages):
            page = original_pdf.getPage(i)
            if i == last_page_index:
                page.mergePage(signature_pdf.getPage(0))
            writer.addPage(page)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return base64.b64encode(output_stream.read())
