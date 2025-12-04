from odoo import api, fields, models
from ..odoo_utils import fns_chatter


class AssignCorrespondence(models.TransientModel):
    _name = "correspondence.dialog.assign"
    _description = "Asignar correspondencia"

    reason_id = fields.Many2one("correspondence.reason", string="Motivo", required=True)

    parent_correspondence_id = fields.Many2one(
        "correspondence.message", string="Correspondencia anterior"
    )
    correspondence_issue = fields.Char(string="Asunto")
    from_partner_id = fields.Many2one("res.partner", string="De")
    to_partner_id = fields.Many2one("res.partner", string="A")

    from_employee_id = fields.Many2one(
        "hr.employee", string="De", default=lambda self: self.env.user.employee_id.id
    )
    to_employee_id = fields.Many2one("hr.employee", string="A")

    from_id_is_external = fields.Boolean(string="De: es externo", default=False)
    to_id_is_external = fields.Boolean(string="A: es externo", default=False)

    action_id = fields.Many2one("correspondence.action", string="Actividad")
    document_ids = fields.Many2many(
        "correspondence.document",
        string="Documento",
        domain="[('correspondence_message_id', '=', None), ('reason_id', '=?', reason_id)]",
        default=lambda self: self.env["correspondence.document"].search(
            [
                ("correspondence_message_id", "=", None),
                ("reason_id", "=", self.env.context.get("default_reason_id")),
            ]
        ),
    )

    page_quantity = fields.Integer(string="Cantidad de hojas")

    @api.onchange("from_employee_id")
    def _onchange_from_employee_id(self):
        self.from_partner_id = self.from_employee_id.user_partner_id.id

    @api.onchange("to_employee_id")
    def _onchange_to_employee_id(self):
        self.to_partner_id = self.to_employee_id.user_partner_id.id

    def action_confirm(self):
        """
        If there is no parent correspondence, then it is a new correspondence.
        If there is a parent correspondence and the action is set, then it is a new correspondence.
        If there is a parent correspondence and the action is NOT set, then
           Update the parent correspondence with the new info.
        """
        self.ensure_one()

        if self._is_new_correspondence():
            correspondence_record = self._create_new_correspondence()
        else:
            correspondence_record = self._update_parent_correspondence()

        self._post_into_chatter_related_info(correspondence_record)

        self.reason_id.set_sequence()

        return True

    def _is_new_correspondence(self):
        if (
            self.parent_correspondence_id.exists()
            and not self.parent_correspondence_id.action_id.exists()
        ):
            return False
        return True

    def _create_new_correspondence(self):
        constructor_dict = {
            "ref": self.correspondence_issue,
            "reason_id": self.reason_id.id,
            "from_employee_id": self.from_employee_id.id,
            "to_employee_id": self.to_employee_id.id,
            "sent_date": fields.Datetime.now(),
        }
        if self.from_partner_id.exists():
            constructor_dict["from_partner_id"] = self.from_partner_id.id
        if self.to_partner_id.exists():
            constructor_dict["to_partner_id"] = self.to_partner_id.id
        if self.page_quantity:
            constructor_dict["quantity_pages"] = self.page_quantity
        if self.action_id.exists():
            constructor_dict["action_id"] = self.action_id.id
            constructor_dict["state"] = "sent"
        # Create correspondence
        correspondence_record = self.env["correspondence.message"].create(constructor_dict)

        # Update parent correspondence if it exists
        if self.parent_correspondence_id.exists():
            self.parent_correspondence_id.state = "done"

        return correspondence_record

    def _update_parent_correspondence(self) -> models.Model:
        correspondence_record = self.parent_correspondence_id
        correspondence_record.name = self.correspondence_issue
        correspondence_record.sent_date = fields.Datetime.now()
        correspondence_record.from_partner_id = self.from_partner_id.id
        correspondence_record.to_partner_id = self.to_partner_id.id
        correspondence_record.from_employee_id = self.from_employee_id.id
        correspondence_record.to_employee_id = self.to_employee_id.id
        correspondence_record.quantity_pages = self.page_quantity
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
