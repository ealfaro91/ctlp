from odoo import api, exceptions, fields, models


class Correspondence(models.Model):
    """
    Correspondence
    - If the correspondence has `todo` state
        - You can create a document
        - You can create an action (Assign forward to user)
    - If the correspondence has an `action`
        - You can not create a document
        - The `state` change to `sent`
    - The correspondence can be assigned to a user
        - the destination user can mark as `assigned`
        - The user can attach documents, and make some actions
    - The user can resolve/close/finish the correspondence marking as `done`
    State diagram:
    todo -> sent -> assigned -> done
              ^         |    ->
              ----------|
    """

    _name = "correspondence.message"
    _description = "Mensaje de correspondencia"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id DESC"

    # Meta Info
    reason_id = fields.Many2one(
        "correspondence.reason", string="Motivo principal", required=True, tracking=True
    )
    name = fields.Char(
        string="Mensaje", tracking=True, default="Nuevo", store=True, compute="_set_sequence"
    )
    ref = fields.Char(string="Referencia / Asunto", tracking=True)

    sent_date = fields.Datetime(string="Fecha de envio", tracking=True)
    received_date = fields.Datetime(string="Fecha de recepción", tracking=True)

    state = fields.Selection(
        [
            ("todo", "Por destinar"),
            ("sent", "Enviado / Para recepcionar"),
            ("assigned", "Recepcionado"),
            ("done", "Finalizado"),
            ("closed", "Cerrado"),
        ],
        required=True,
        default="todo",
        string="Estado",
    )

    all_correspondence_ids = fields.One2many(
        "correspondence.message",
        related="reason_id.correspondence_message_ids",
        string="Todas las correspondencias",
    )

    from_employee_id = fields.Many2one("hr.employee", string="De:", tracking=True)
    to_employee_id = fields.Many2one("hr.employee", string="A:", tracking=True)

    from_partner_id = fields.Many2one("res.partner", string="De:", tracking=True)
    to_partner_id = fields.Many2one("res.partner", string="A:", tracking=True)

    from_user_id = fields.Many2one(
        "res.users", string="De:", tracking=True, compute="_update_user_id", store=True
    )

    to_user_id = fields.Many2one(
        "res.users", string="A:", tracking=True, compute="_update_user_id", store=True
    )

    action_id = fields.Many2one("correspondence.action", string="Actividad", tracking=True)
    document_ids = fields.One2many(
        "correspondence.document",
        inverse_name="correspondence_message_id",
        string="Documento de correspondencia",
        tracking=True,
    )

    all_document_ids = fields.One2many(
        "correspondence.document",
        related="reason_id.document_ids",
        string="Todos los documentos",
    )

    # Instance Info
    note = fields.Html(string="Nota", tracking=True)

    # roadmap
    quantity_pages = fields.Integer(string="Cantidad de hojas")

    color = fields.Integer(string="Color", compute="_compute_color", store=True)

    @api.depends("state")
    def _set_sequence(self):
        for record in self:
            if record.state == "sent":
                record.name = (
                    self.env["ir.sequence"].next_by_code("seq.correspondence.message")
                    or "Nuevo"
                )

    @api.depends("to_employee_id", "from_employee_id")
    def _update_user_id(self):
        for record in self:
            if record.from_employee_id.exists():
                record.from_user_id = record.from_employee_id.user_id
            else:
                record.from_user_id = False

            if record.to_employee_id.exists():
                record.to_user_id = record.to_employee_id.user_id
            else:
                record.to_user_id = False

    @api.onchange("to_employee_id")
    def _ui_update_to_id(self):
        for record in self:
            if record.to_employee_id.exists():
                record.to_partner_id = record.to_employee_id.user_partner_id

    @api.onchange("from_employee_id")
    def _ui_update_from_id(self):
        for record in self:
            if record.from_employee_id.exists():
                record.from_partner_id = record.from_employee_id.user_partner_id

    def _compute_color(self):
        for rec in self:
            if rec.state in ["todo"]:
                rec.color = 9
            elif rec.state == "sent":
                rec.color = 3
            elif rec.state == "assigned":
                rec.color = 4
            elif rec.state in ["done", "closed"]:
                rec.color = 10
            else:
                rec.color = 7

    def action_show_correspondence(self):
        self.ensure_one()
        form_id = self.env.ref("sincpro_correspondence.correspondence_form")
        return {
            "type": "ir.actions.act_window",
            "name": "Correspondencia",
            "res_model": "correspondence.message",
            "view_mode": "form",
            "view_id": form_id.id,
            "res_id": self.id,
        }

    def action_assign_correspondence(self):
        self.ensure_one()

        constructor_dict = {
            "reason_id": self.reason_id.id,
            "parent_correspondence_id": self.id,
            "correspondence_issue": self.ref or self.reason_id.issue,
        }

        if not self.action_id.exists():
            if self.from_employee_id.exists():
                constructor_dict["from_employee_id"] = self.from_employee_id.id
            if self.to_employee_id.exists():
                constructor_dict["to_employee_id"] = self.to_employee_id.id

            constructor_dict["page_quantity"] = self.quantity_pages

        record = self.env["correspondence.dialog.assign"].create(constructor_dict)
        record._onchange_from_employee_id()
        record._onchange_to_employee_id()

        return {
            "type": "ir.actions.act_window",
            "name": "Crear Correspondencia",
            "res_model": "correspondence.dialog.assign",
            "view_mode": "form",
            "view_id": self.env.ref("sincpro_correspondence.assign_correspondence_form").id,
            "target": "new",
            "res_id": record.id,
        }

    def action_generate_document(self):
        self.ensure_one()
        constructor_dict = {
            "reason_id": self.reason_id.id,
            "correspondence_id": self.id,
        }
        record = self.env["correspondence.dialog.generate.document"].create(constructor_dict)

        return {
            "type": "ir.actions.act_window",
            "name": "Generar Documento",
            "res_model": "correspondence.dialog.generate.document",
            "view_mode": "form",
            "view_id": self.env.ref("sincpro_correspondence.dialog_generate_document").id,
            "target": "new",
            "res_id": record.id,
        }

    def action_receive_correspondence(self):
        self.ensure_one()
        if self.env.user.has_group("sincpro_correspondence.group_correspondence_manager"):
            self.received_date = fields.Datetime.now()
            self.state = "assigned"
            return

        if self.to_user_id.id != self.env.user.id:
            raise exceptions.UserError(
                "No puedes recibir correspondencia que no te corresponde"
            )
        self.received_date = fields.Datetime.now()
        self.state = "assigned"

    def action_close_correspondence(self):
        self.ensure_one()
        if self.env.user.has_group("sincpro_correspondence.group_correspondence_manager"):
            self.state = "closed"
            return

        if self.to_user_id.id != self.env.user.id:
            raise exceptions.UserError(
                "No puedes recibir correspondencia que no te corresponde"
            )
        self.state = "closed"

    def action_open_mail_composer(self):
        """Opens a wizard to compose an email, with relevant mail template loaded by default"""
        self.ensure_one()
        attachments_ids = self.reason_id.message_ids.attachment_ids.mapped("id")
        print(attachments_ids)
        ctx = {
            "default_model": "correspondence.message",
            "default_res_ids": self.ids,
            "default_subject": self.ref or self.reason_id.issue,
            "default_author_id": self.env.user.partner_id.id,
            "default_partner_ids": self.to_partner_id.ids,
            "default_composition_mode": "comment",
            "mark_so_as_sent": True,
            "default_email_layout_xmlid": "mail.mail_notification_layout_with_responsible_signature",
            "force_email": True,
            "default_attachment_ids": attachments_ids,
        }

        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }
