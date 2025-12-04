from odoo import api, fields, models


class CorrespondenceDocument(models.Model):
    """
    A correspondence can have many documents assigned pear action/assign
    Historical correspondences can have many documents
    """

    _name = "correspondence.document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Documentos de correspondencia"
    _order = "id DESC"

    name = fields.Char(string="Referencia", tracking=True)
    document_type_id = fields.Many2one(
        "correspondence.type",
        required=True,
        string="Tipo de documento",
    )
    reason_id = fields.Many2one("correspondence.reason", string="Motivo")

    correspondence_message_id = fields.Many2one(
        "correspondence.message",
        string="Correspondencia",
        tracking=True,
    )

    state = fields.Selection(
        [("no_assigned", "No asignado"), ("assigned", "Asignado")],
        string="Estado",
        default="no_assigned",
        compute="_compute_state",
        store=True,
        tracking=True,
    )
    to_employee_id = fields.Many2one("hr.employee", string="A:", tracking=True)
    via_employee_id = fields.Many2one("hr.employee", string="Via:", tracking=True)
    from_employee_ids = fields.Many2many(
        "hr.employee",
        "document_from_employee_rel",
        "document_id",
        "employee_id",
        string="De:",
    )

    is_external = fields.Boolean(string="Es externo", tracking=True)
    elaborated_by_partner_id = fields.Many2one(
        "res.partner", string="Elaborado por", tracking=True
    )
    to_partner_id = fields.Many2one("res.partner", string="Destinatario", tracking=True)

    employees_to_approve_ids = fields.Many2many(
        "hr.employee",
        "document_to_approve_employee_rel",
        "document_id",
        "employee_id",
        string="Aprobadores",
    )

    place = fields.Char(string="Lugar", tracking=True)
    date = fields.Datetime(string="Fecha", default=fields.Datetime.now(), tracking=True)

    @api.depends("correspondence_message_id")
    def _compute_state(self):
        for record in self:
            if record.correspondence_message_id.exists():
                record.state = "assigned"
            else:
                record.state = "no_assigned"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            correspondence_type = "document_type_id" in vals and self.env[
                "correspondence.type"
            ].browse(vals["document_type_id"])
            # if correspondence_type.exists():
            #     vals["name"] = correspondence_type.sequence_id.next_by_id()
        return super().create(vals_list)

    def action_download_word(self):
        # Download the word
        pass

    def action_download_pdf(self):
        pass

    def action_show_correspondence_document(self):
        self.ensure_one()
        form_id = self.env.ref("sincpro_correspondence.sp_correspondence_doc_form_view")
        return {
            "type": "ir.actions.act_window",
            "name": "Correspodencia",
            "res_model": "correspondence.document",
            "view_mode": "form",
            "view_id": form_id.id,
            "res_id": self.id,
        }
