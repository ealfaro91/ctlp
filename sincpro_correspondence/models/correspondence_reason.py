from odoo import fields, models

TYPE_CORRESPONDENCE = [("internal", "Interno"), ("external", "Externo")]


class Reason(models.Model):
    _name = "correspondence.reason"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Motivo o asunto"
    _order = "id DESC"

    name = fields.Char(string="Referencia", tracking=True, default="Nuevo", store=True)
    issue = fields.Char(string="Asunto", required=True, tracking=True)
    origin = fields.Char(string="Origen/Referencia", tracking=True)
    date = fields.Date(
        string="Fecha", required=True, default=fields.Date.today(), tracking=True
    )

    type = fields.Selection(TYPE_CORRESPONDENCE, string="Tipo", required=True, tracking=True)

    state = fields.Selection(
        [("draft", "Borrador"), ("done", "Generado"), ("cancel", "Cancelado")],
        string="Estado",
        default="draft",
        tracking=True,
    )

    correspondence_message_ids = fields.One2many(
        "correspondence.message", "reason_id", string="Correspondencias"
    )

    count_correspondence = fields.Integer(
        string="Cantidad de Correspondencias",
        compute="_compute_count_correspondence",
    )

    document_ids = fields.One2many(
        "correspondence.document", "reason_id", string="Documentos"
    )

    def action_assign_correspondence(self):
        self.ensure_one()
        default_context = {
            "default_reason_id": self.id,
            "default_correspondence_issue": self.issue,
            "default_from_employee_id": self.env.user.employee_id.id,
        }

        return {
            "type": "ir.actions.act_window",
            "name": "Crear Correspondencia",
            "res_model": "correspondence.dialog.assign",
            "view_mode": "form",
            "view_id": self.env.ref("sincpro_correspondence.assign_correspondence_form").id,
            "target": "new",
            "context": default_context,
        }

    def action_generate_document(self):
        self.ensure_one()
        default_context = {
            "default_reason_id": self.id,
        }

        return {
            "type": "ir.actions.act_window",
            "name": "Generar Documento",
            "res_model": "correspondence.dialog.generate.document",
            "view_mode": "form",
            "view_id": self.env.ref("sincpro_correspondence.dialog_generate_document").id,
            "target": "new",
            "context": default_context,
        }

    def set_sequence(self):
        for record in self:
            if record.state == "draft":
                if record.type == "external":
                    sequence = (
                        self.env["ir.sequence"]
                        .sudo()
                        .next_by_code("seq.correspondence.roadmap")
                    )
                    record.name = sequence
                if record.type == "internal":
                    sequence = (
                        self.env["ir.sequence"]
                        .sudo()
                        .next_by_code("seq.correspondence.issue")
                    )
                    record.name = sequence
                record.state = "done"
            else:
                record.name = record.name
        self.env.cr.commit()

    def action_redirect_correspondence(self):
        self.ensure_one()
        if (
            self.correspondence_message_ids.exists()
            and len(self.correspondence_message_ids) == 1
        ):
            return {
                "type": "ir.actions.act_window",
                "name": "Correspondencia",
                "res_model": "correspondence.message",
                "view_mode": "form",
                "res_id": self.correspondence_message_ids.id,
            }

        if self.correspondence_message_ids.exists():
            return {
                "type": "ir.actions.act_window",
                "name": "Correspondencia",
                "res_model": "correspondence.message",
                "view_mode": "tree,form",
                "domain": [("reason_id", "=", self.id)],
            }

    def _compute_count_correspondence(self):
        for record in self:
            record.count_correspondence = len(record.correspondence_message_ids)
