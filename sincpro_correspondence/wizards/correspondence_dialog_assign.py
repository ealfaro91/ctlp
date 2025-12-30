from odoo import api, fields, models
from ..odoo_utils import fns_chatter


class CorrespondenceDialogAssign(models.TransientModel):
    _name = "correspondence.dialog.assign"
    _description = "Asignar correspondencia"

    reason_id = fields.Many2one(
        "correspondence.reason",
        string="Motivo",
        required=True
    )
    message_id = fields.Many2one(
        "correspondence.message",
        string="Correspondencia",
    )
    parent_correspondence_id = fields.Many2one(
        "correspondence.message",
        string="Correspondencia anterior"
    )
    correspondence_issue = fields.Char(string="Asunto")
    from_user_id = fields.Many2one(
        "res.users", string="De",
        domain=[("share", "=", False)],
        required=True,
        default=lambda self: self.env.user.id
    )
    to_user_id = fields.Many2one(
        "res.users", string="A",
        domain=[("share", "=", False)],
        required=True
    )
    area_from = fields.Char(
        string="Area remitente",
        related="from_user_id.area",
        store=True
    )
    area_to = fields.Char(
        string="Area destinatario",
        related="to_user_id.area",
        store=True
    )
    action_id = fields.Many2one(
        "correspondence.action",
        string="Actividad"
    )
    activity_id = fields.Many2one(
        "mail.activity.type",
        string="Actividad"
    )
    document_ids = fields.Many2many(
        "ir.attachment",
        "correspondence_assign_document_rel",
        "assign_id",
        "attachment_id",
        string="Documentos a enviar",
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "correspondence_assign_attachment_rel",
        "assign_id",
        "attachment_id",
        string="Adjuntos",
    )
    reason = fields.Text(string="Motivo Finalización/Archivado")


    def action_confirm(self):
        """
        If there is no parent correspondence, then it is a new correspondence.
        If there is a parent correspondence and the action is set, then it is a new correspondence.
        If there is a parent correspondence and the action is NOT set, then
           Update the parent correspondence with the new info.
        """
        self.ensure_one()
        if self._context.get('is_close'):
            self.message_id.state = "done"
            self.message_id.reason = self.reason
            return
        if self.parent_correspondence_id:
            if  self._context.get('is_reassign'):
                self.parent_correspondence_id.state = "reassigned"
                self.message_id.reason = self.reason
        self._create_new_correspondence()
        return True

    def _is_new_correspondence(self):
        if (
            self.parent_correspondence_id.exists()
            and not self.parent_correspondence_id.action_id.exists()
        ):
            return False
        return True

    def _create_new_correspondence(self):
       # self.messaged
        constructor_dict = {
            "ref": self.correspondence_issue,
            "reason_id": self.reason_id.id,
            "from_user_id": self.from_user_id.id,
            "to_user_id": self.to_user_id.id,
            "sent_date": fields.Datetime.now(),
            "activity_id": self.activity_id.id,
            "document_ids": self.document_ids.ids,
            "reason": self.reason,
        #    "parent_correspondence_id": self.parent_correspondence_id.id,
            "attachment_ids": self.attachment_ids.ids,
        }
        correspondence_record = self.env["correspondence.message"].create(constructor_dict)
        #
        # # Update parent correspondence if it exists
        # if self.parent_correspondence_id.exists():
        #     self.parent_correspondence_id.state = "done"

        return correspondence_record

    def _update_parent_correspondence(self) -> models.Model:
        correspondence_record = self.parent_correspondence_id
        correspondence_record.name = self.correspondence_issue
        correspondence_record.sent_date = fields.Datetime.now()
        correspondence_record.from_partner_id = self.from_partner_id.id
        correspondence_record.to_partner_id = self.to_partner_id.id
        correspondence_record.from_user_id = self.from_user_id.id
        correspondence_record.to_user_id = self.to_user_id.id
        correspondence_record.quantity_pages = self.page_quantity
        if self.document:
            correspondence_record.document = self.document
            correspondence_record.document_filename = self.document_name
        if self.action_id.exists():
            correspondence_record.action_id = self.action_id.id
            correspondence_record.state = "sent"

        return correspondence_record

    def _post_into_chatter_related_info(self, correspondence_record):
        if not self._is_new_correspondence():
            # if it is not a new correspondence, not post anything, previously was updated
            return

        correspondence_record.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": correspondence_record, "origin": self.reason_id},
            subtype_xmlid="mail.mt_note",
        )

        fns_chatter.post_into_chatter_link_record(
            self.reason_id,
            correspondence_record,
            self.env,
        )

        if self.document_ids.exists():
            correspondence_record.document_ids = self.document_ids
            correspondence_record.message_post_with_source(
                "mail.message_origin_link",
                render_values={"self": correspondence_record, "origin": self.document_ids},
                subtype_xmlid="mail.mt_note",
            )
