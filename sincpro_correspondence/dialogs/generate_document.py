import base64
from typing import Tuple

from odoo import SUPERUSER_ID, api, fields, models
from ..odoo_utils import fns_chatter

from ..word_docs import correspondence_docx


class GenerateDocument(models.TransientModel):
    _name = "correspondence.dialog.generate.document"
    _description = "Generar documento"

    reason_id = fields.Many2one("correspondence.reason", string="Motivo")
    correspondence_id = fields.Many2one("correspondence.message", string="Correspondencia")
    auto_associate_to_correspondence = fields.Boolean(
        string="Asociar documento a correspondencia",
        default=False,
        help="por defecto si estas creadon un documento desede una correspondencia se asociara de forma directa",
    )

    correspondence_type_id = fields.Many2one(
        "correspondence.type", string="Tipo de correspondencia"
    )

    # Internal
    to_employee_id = fields.Many2one("hr.employee", string="A:")
    via_employee_id = fields.Many2one("hr.employee", string="Via:")
    from_employee_ids = fields.Many2many(
        "hr.employee",
        "dialog_employee_ids",
        "dialog_document_id",
        "employee_id",
        string="De:",
    )

    # For document
    is_external = fields.Boolean(string="Es externo")
    elaborated_by_partner_id = fields.Many2one(
        "res.partner",
        string="Elaborado por:",
        default=lambda self: self.env.user.partner_id.id,
    )
    to_partner_id = fields.Many2one("res.partner", string="Para:")

    employees_to_approve_ids = fields.Many2many(
        "hr.employee",
        "dialog_employee_to_approve_ids",
        "dialog_document_id",
        "employee_id",
        string="Aprobadores",
    )

    place = fields.Char(string="Lugar")
    date = fields.Datetime(string="Fecha", default=fields.Datetime.now())

    @api.onchange("from_employee_ids")
    def _onchange_from_employee_ids(self):
        for rec in self:
            rec.employees_to_approve_ids = rec.from_employee_ids

    def action_confirm(self):
        """
        Take into account the document records should be present in the following models:
        - correspondence.message
        - correspondence.reason
        """
        self.ensure_one()
        constructor_dict = {
            "document_type_id": self.correspondence_type_id.id,
            "to_employee_id": self.to_employee_id.id,
            "via_employee_id": self.via_employee_id.id,
            "from_employee_ids": [(6, 0, self.from_employee_ids.ids)],
            "is_external": self.is_external,
            "elaborated_by_partner_id": self.elaborated_by_partner_id.id,
            "to_partner_id": self.to_partner_id.id,
            "employees_to_approve_ids": [(6, 0, self.employees_to_approve_ids.ids)],
            "place": self.place,
            "date": self.date,
        }

        if self.reason_id.exists():
            constructor_dict["reason_id"] = self.reason_id.id

        # Create document
        document_record = self.env["correspondence.document"].create(constructor_dict)
        self.reason_id.set_sequence()
        self._post_info_to_chatter(document_record)

        return True

    def _post_info_to_chatter(self, document_record):
        attachment_id, word_bytes = self._generate_word_docx(document_record)

        fns_chatter.post_into_chatter_link_record(
            self.reason_id,
            document_record,
            self.env,
        )

        fns_chatter.post_message_with_attachments_ids_in_chatter(
            self.reason_id,
            "Adjuntando documento a la razón de correspondencia",
            [attachment_id],
            self.env.user.partner_id.id or SUPERUSER_ID,
        )
        fns_chatter.post_message_with_attachments_ids_in_chatter(
            document_record,
            "Adjuntando documento a la razón de correspondencia",
            [attachment_id],
            self.env.user.partner_id.id or SUPERUSER_ID,
        )

    def _generate_word_docx(self, document_record) -> Tuple[int, bytes]:
        word_bytes: bytes = correspondence_docx.build_word_docx(document_record)
        ir_values = {
            "name": f"{document_record.name}.docx",
            "type": "binary",
            "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "datas": base64.b64encode(word_bytes),
            "raw": word_bytes,
            "store_fname": f"{document_record}.docx",
        }
        word_attachment = self.env["ir.attachment"].sudo().create(ir_values)

        return (
            word_attachment.id,
            word_bytes,
        )
