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
        "correspondence.reason",
        string="Motivo principal",
        required=True,
        tracking=True
    )
    reason_state = fields.Selection(
        related="reason_id.state",
        string="Estado",
        store=True,
    )
    name = fields.Char(
        string="Mensaje",
        tracking=True,
        default="Nuevo",
        store=True,
        compute="_set_sequence"
    )
    ref = fields.Char(
        string="Referencia / Asunto",
        tracking=True
    )
    sent_date = fields.Datetime(
        string="Fecha de envio",
        tracking=True
    )
    received_date = fields.Datetime(
        string="Fecha de recepción",
        tracking=True
    )
    state = fields.Selection([
         ("todo", "Por destinar"),
         ("sent", "Enviado / Para recepcionar"),
         ("assigned", "Recepcionado"),
         ("done", "Finalizado"),
         ("reassigned", "Reasignado")
    ],
        required=True,
        default="todo",
        string="Estado",
    )
    reason = fields.Text(
        string="Motivo Finalización/Archivado",
        tracking=True
    )


    all_correspondence_ids = fields.One2many(
        "correspondence.message",
        related="reason_id.correspondence_message_ids",
        string="Todas las correspondencias",
    )
    company_id = fields.Many2one("res.company")
    from_user_id = fields.Many2one(
        "res.users",
        string="De:",
        tracking=True,
        required=True,
        domain=[("share", "=", False)],
    )
    to_user_id = fields.Many2one(
        "res.users",
        string="A:",
        tracking=True,
        required=True,
        domain=[("share", "=", False)],
    )
    area_from = fields.Char(
        string="Area remitente",
        related="from_user_id.area"
    )
    area_to = fields.Char(
        string="Area destinatario",
        related="to_user_id.area"
    )
    action_id = fields.Many2one(
        "correspondence.action",
        string="Actividad",
        tracking=True
    )
    activity_id = fields.Many2one(
        "mail.activity.type",
        string="Actividad",
        tracking=True
    )
    document_ids = fields.Many2many(
        "ir.attachment",
        "correspondence_message_document_rel",
        "correspondence_message_id",
        "attachment_id",
        string="Adjuntos",
    )

    attachment_ids = fields.Many2many(
        "ir.attachment",
        "correspondence_message_attachment_rel",
        "correspondence_message_id",
        "attachment_id",
        string="Correspondencia",
    )

    # all_document_ids = fields.One2many(
    #     "correspondence.document",
    #     related="reason_id.document_ids",
    #     string="Todos los documentos",
    # )

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

    # @api.depends("to_user_id", "from_user_id")
    # def _update_user_id(self):
    #     for record in self:
    #         if record.from_user_id.exists():
    #             record.from_user_id = record.from_user_id.user_id
    #         else:
    #             record.from_user_id = False
    #
    #         if record.to_user_id.exists():
    #             record.to_user_id = record.to_user_id.user_id
    #         else:
    #             record.to_user_id = False

    # @api.onchange("to_user_id")
    # def _ui_update_to_id(self):
    #     for record in self:
    #         if record.to_user_id.exists():
    #             record.to_partner_id = record.to_user_id.user_partner_id

    # @api.onchange("from_user_id")
    # def _ui_update_from_id(self):
    #     for record in self:
    #         if record.from_user_id.exists():
    #             record.from_partner_id = record.from_user_id.user_partner_id

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
        form_id = self.env.ref("sincpro_correspondence.correspondence_form_view")
        return {
            "type": "ir.actions.act_window",
            "name": "Correspondencia",
            "res_model": "correspondence.message",
            "view_mode": "form",
            "view_id": form_id.id,
            "res_id": self.id,
        }

    def action_assign_correspondence(self):
        if self.state == "done":
            return {
                "type": "ir.actions.act_window",
                "name": "Correspondencia",
                "res_model": "correspondence.dialog.assign",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "is_reassign": True,
                    "default_parent_correspondence_id": self.id,
                    "default_from_user_id": self.from_user_id.id,
                    "default_reason_id": self.reason_id.id,
                    "default_message_id": self.id,
                    "default_attachment_ids": self.attachment_ids.ids
                },
            }

        self.ensure_one()
        self.state = "sent"
        mail_template = self.env.ref(
            "sincpro_correspondence.correspondence_delegation", raise_if_not_found=True
        )
        mail_template.attachment_ids = self.attachment_ids
        mail_template.send_mail(
            self.id, force_send=False, raise_exception=True
        )

        # constructor_dict = {
        #     "reason_id": self.reason_id.id,
        #     "parent_correspondence_id": self.id,
        #     "correspondence_issue": self.ref or self.reason_id.issue,
        # }
        #
        # if not self.action_id.exists():
        #     if self.from_user_id.exists():
        #         constructor_dict["from_user_id"] = self.from_user_id.id
        #     if self.to_user_id.exists():
        #         constructor_dict["to_user_id"] = self.to_user_id.id
        #
        #     constructor_dict["page_quantity"] = self.quantity_pages
        #
        # record = self.env["correspondence.dialog.assign"].create(constructor_dict)
        # record._onchange_from_employee_id()
        # record._onchange_to_employee_id()

        # return {
        #     "type": "ir.actions.act_window",
        #     "name": "Crear Correspondencia",
        #     "res_model": "correspondence.dialog.assign",
        #     "view_mode": "form",
        #     "view_id": self.env.ref("sincpro_correspondence.assign_correspondence_form").id,
        #     "target": "new",
        #     "res_id": record.id,
        # }


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
       # self.state = "done"
        return {
            "type": "ir.actions.act_window",
            "name": "Correspondencia",
            "res_model": "correspondence.dialog.assign",
            "view_mode": "form",
            "target": "new",
            "context": {
                "is_close": True,
                "default_parent_correspondence_id": self.id,
                "default_from_user_id": self.from_user_id.id,
                "default_reason_id": self.reason_id.id,
                "default_message_id": self.id,
                "default_attachment_ids": self.attachment_ids.ids
            },
        }

    def action_open_mail_composer(self):
        """Opens a wizard to compose an email, with relevant mail template loaded by default"""
        self.ensure_one()
        # attachments_ids = self.reason_id.message_ids.attachment_ids.mapped("id")
        # attachment = self.env["ir.attachment"].create({
        #     "name": self.document_name,
        #     "type": "binary",
        #     "datas": self.document,  # tu binario en base64
        #     "mimetype": "application/pdf",
        #     "res_model": "tu.modelo",
        #     "res_id": self.id,})
        ctx = {
            "default_model": "correspondence.message",
            "default_res_ids": self.ids,
            "default_subject": self.ref or self.reason_id.issue,
            "default_author_id": self.env.user.partner_id.id,
            "default_partner_ids": self.to_partner_id.ids,
            "default_composition_mode": "comment",
            "mark_so_as_sent": True,
            "default_email_layout_xmlid": "sincpro_correspondence.correspondence_delegation",
            "force_email": True,
            "default_attachment_ids": self.attachment_ids.ids,
            #"default_attachment_ids": attachments_ids,
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
