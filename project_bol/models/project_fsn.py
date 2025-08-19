
import base64
import io

#from PyPDF2 import PdfReader, PdfWriter
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.utils import ImageReader
# from reportlab.lib import colors

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectFsn(models.Model):
    _name = "project.fsn"
    _description = "Project FSN (Needs Request Form)"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin",]
    _order = "create_date desc"

    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
        help="Indicates whether this Needs Request Form is active or not."
    )
    name = fields.Char(
        string="Title",
        required=True,
        tracking=True,
        translate=True,
        help="The name of the Needs Request Form."
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
        tracking=True,
        help="The company this ticket is related to.",
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
    problem_identification = fields.Text(
        string="Problem Identification",
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
    approval_log_ids = fields.One2many(
        "approval.log", "project_fsn_id",
        string="Approval Log ids",
    )
    sent_approval_request = fields.Boolean(
        string="Sent Approval Request",
        default=False,
        help="Indicates whether the approval request has been sent."
    )
    state = fields.Selection([
        ("to_approve", "To Approve"),
        ("approval_request", "Approval Request Sent"),
        ("approved", "Approved")],
        string="Status",
        default="to_approve",
        store=True,
        compute="_compute_approval_state",
    )
    document_filename = fields.Char(
        string="Document File Name",
        tracking=True
    )
    document = fields.Binary(
        string="Document",
        attachment=True,
        required=True,
    )
    document_signed = fields.Binary(
        string="Signed Document",
        attachment=True,
    )
    document_signed_filename = fields.Char(
        string="Document Signed File Name",
        tracking=True
    )
    document_url = fields.Char(
        compute="get_document_url", string="Portal Access Link"
    )

    @api.depends("approval_log_ids")
    def _compute_approval_state(self):
        """Compute the approval state based on the approval
         log and create a project if all approvals are done."""
        for fsn in self:
            fsn.approved = False
            if fsn.approval_log_ids:
                fsn.state = "approved" if all(
                    log.state == "approved" for log in fsn.approval_log_ids
                ) else "to_approve" if not fsn.sent_approval_request else "approval_request"
                if fsn.state == "approved":
                    mail_template = self.env.ref(
                        "project_bol.fsn_approved_notification", raise_if_not_found=True
                    )
                    mail_template.sudo().send_mail(fsn.id, force_send=False, raise_exception=True)
                    fsn._action_create_project()

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

    def _get_portal_return_action(self):
        """Return the action used to display record when returning from customer portal."""
        self.ensure_one()
        return self.env.ref("project_bol.approval_log_action")

    def get_portal_sign_url(self):
        return "/my/fsn/%s/sign?access_token=%s" % (self.id, self.access_token)

    def button_send_approval_request(self):
        """Send approval request emails to all users in the approval log.
        returns a notification message."""

        for rec in self:
            if not rec.approval_log_ids:
                raise ValidationError(
                    _("There are no users in the approval log to send the request.")
                )
            for user in rec.approval_log_ids.mapped("user_id"):
                mail_template = self.env.ref(
                    "project_bol.fsn_approval_request_email", raise_if_not_found=True
                )
                # Aquí estamos pasando al contexto el usuario
                mail_template.sudo().with_context(
                    email_to=user.email_formatted,
                    user_id=user
                ).send_mail(
                    rec.id, force_send=False, raise_exception=True
                )
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

    def _action_create_project(self):
        """Creates a project with fsn values."""
        self.ensure_one()
        project = self.env["project.project"].create({
            "name": self.name,
            "description": self.incident_description,
            "requested_by_id": self.requested_by_id.id,
            "fsn_id": self.id,
            "requested_by_id": self.requested_by_id.id,
            "date_start": self.date_start_project,
            "date": self.date_end_project,
            "requested_area": self.area
        })
        self.project_id = project.id
        mail_template = self.env.ref(
            "project_bol.project_creation_email", raise_if_not_found=True
        )
        mail_template.sudo().with_context(
            email_to=user.email_formatted,
        ).send_mail(self.project_id.id, force_send=True, raise_exception=True)

    @api.model
    def get_dashboard_values(self):
        """This method returns values to the dashboard in project views."""
        result = {
            "to_request_approval": 0,
            "my_fsn": 0,
        }
        fsn = self.env["project.fsn"]

        result["today_appointments"] = appointments.search_count(
            [("init_date", "=", fields.Date.context_today(self))]
        )
        result["my_appointments"] = appointments.search_count(
            [
                ("init_date", "=", fields.Date.context_today(self)),
                "|",
                "|",
                ("monitoring_user_id", "=", self.env.user.id),
                ("medical_user_id", "=", self.env.user.id),
                ("user_ids", "in", self.env.user.id),
            ]
        )
        return result


