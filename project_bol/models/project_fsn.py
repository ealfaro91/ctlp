
from odoo import models, fields, api


class ProjectFsn(models.Model):
    _name = "project.fsn"
    _description = "Project FSN (Functional Specification Note)"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin",]

    name = fields.Char(
        string="Title",
        required=True,
        tracking=True,
        translate=True,
        help="The name of the Functional Specification Note."
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        tracking=True,
        help="The project this ticket is related to.",
    )
    date_start_project = fields.Datetime(
        string="Date Start Project",
        tracking=True,
        help="The date when the project is expected to start.",
    )
    date_end_project = fields.Datetime(
        string="Date End Project",
        tracking=True,
        help="The date when the project is expected to end.",
    )
    area = fields.Char(
        related="requested_by_id.area",
        string="Area",
        tracking=True,
        help="The area related to the user who requested this ticket."
    )
    requested_by_id = fields.Many2one(
        "res.users",
        string="Requested By",
        tracking=True,
        required=True,
        default=lambda self: self.env.user,
        help="The user who requested this ticket.",
    )
    date_requested = fields.Datetime(
        string="Date Requested",
        tracking=True,
        required=True,
        default=lambda self: fields.Datetime.now(),
        help="The date when this ticket was requested.",
    )
    version = fields.Char(
        string="Version",
        tracking=True,
        required=True,
        help="The version of the project this ticket is related to.",
    )
    incident_description = fields.Text(
        string="Incident Description",
        tracking=True,
        required=True,
        help="A description of the incident related to this ticket.",
    )
    request_objective = fields.Text(
        string="Request Objective",
        tracking=True,
        required=True,
        help="The objective of the request related to this ticket.",
    )
    request_description = fields.Text(
        string="Request Description",
        tracking=True,
        required=True,
        help="A detailed description of the request related to this ticket.",
    )
    controls_exceptions_assumptions = fields.Text(
        string="Controls/exceptions/assumptions",
        tracking=True,
        required=True,
        help="Details about controls, exceptions, and assumptions related to this ticket.",
    )
    strategic_alignment = fields.Text(
        string="Strategic Alignment",
        tracking=True,
        required=True,
        help="How this ticket aligns with the strategic goals of the organization.",
    )
    problem_or_incident_identification = fields.Text(
        string="Problem or Incident Identification",
        tracking=True,
        required=True,
        help="Identification of the problem or incident related to this ticket.",
    )
    problem_incident_recurrence = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Problem/Incident Recurrence",
        default="no",
        tracking=True,
        required=True,
        help="Indicates if the problem or incident has recurred.",
    )
    affected_system_id = fields.Many2one(
        "project.fsn.system",
        string="Affected System",
        tracking=True,
        required=True,
        help="The system affected by this ticket."
    )
    request_benefits_ids = fields.Many2many(
        "project.fsn.benefit",
        string="Request Benefits",
        tracking=True,
        required=True,
        help="The benefits expected from this request.",
    )
    approval_state_id = fields.Many2one(
        "approval.state",
        string="Approval State",
        domain="[('id', 'in', approval_state_ids)]",
        compute="_compute_approval_state",
        tracking=True
    )
    approval_state_ids = fields.Many2many(
        "approval.state",
        string="Approval State",
        compute="_compute_approval_state_ids",
    )
    approval_log_ids = fields.One2many(
        "approval.log", "project_fsn_id",
        string="Approval Log ids",
    )
    approved = fields.Boolean(
        string="Approved",
        store=True,
        compute="_compute_approval_state",
    )
    document_filename = fields.Char(string="Document File Name", tracking=True)
    document = fields.Binary(string="Document")
    document_url = fields.Char(
        compute="get_document_url", string="Portal Access Link"
    )

    def _compute_approval_state_ids(self):
        """Compute the approval states based on the model."""
        for rec in self:
            rec.approval_state_ids = self.env["approval.state"].search([
                ("model_id", "=", self.env["ir.model"]._get_id("project.fsn"))
            ])

    @api.depends("approval_log_ids")
    def _compute_approval_state(self):
        """ Ensure approvals are done in order. """
        for fsn in self:
            fsn.approved = False
            pending = self.env.ref("project_bol.order_approval_state_pending",  raise_if_not_found=False)
            if not fsn.approval_log_ids:
                if pending:
                    fsn.approval_state_id = pending.id
            else:
                approved = fsn.approval_log_ids.filtered(lambda x: x.state == "approved")
                fsn.approval_state_id = fsn.approval_state_ids.filtered(
                    lambda x: x.role_id == approved[0].role_id)
                fsn.approved = True

    def get_document_url(self):
        """Generate the URL for the document in the portal."""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            if not rec.access_token:
                rec._portal_ensure_token()
            rec.document_url = "%s/my/fsn/%s?access_token=%s" % (
                base_url,
                rec.id,
                rec.access_token,
            )

    def create(self, vals):
        res = super(ProjectFsn, self).create(vals)
        mail_template = self.env.ref(
            "project_bol.fsn_approval_email", raise_if_not_found=False
        )
        mail_template.partner_to = res.approval_state_ids[0].user_id.partner_id.id
        mail_template.send_mail(
            self.env.user.id, force_send=True, raise_exception=False
        )
        return res

    def button_approve(self):
        self.apprved = True
        self._action_create_project()

    def _action_create_project(self):
        """Create a project from the ticket."""
        self.ensure_one()
        project = self.env["project.project"].create({
            "name": self.name,
            "description": self.description,
            "user_id": self.requested_by_id.id,
            "fsn_id": self.id,
            "requested_by_id": self.requested_by_id.id,
            "date_start": self.date_start_project,
            "date_end": self.date_end_project,
            "requested_area_id": self.area_id.id
        })
        self.project_id = project.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "res_id": project.id,
            "view_mode": "form",
            "target": "current",
        }

