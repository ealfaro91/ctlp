
from odoo import fields, models, api, _


class ProjectProject(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "mail.tracking.duration.mixin"]
    _track_duration_field = "stage_id"

    fsn_id = fields.Many2one(
        "project.fsn",
        string="Needs Request Form",
        tracking=True,
        help="The Needs Request Form related to this project.",
    )
    executer_area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Executer Area",
        tracking=True,
        required=False,
        help="The area responsible for executing this project.",
    )
    product_owner_id = fields.Many2one(
        "res.users",
        string="Product Owner",
        tracking=True,
        required=False,
        help="The user who is the product owner for this project.",
    )
    requested_area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Company Area",
        tracking=True,
        required=False,
        help="The area that requested this project.",
    )
    requested_area = fields.Char(
        string="Requested Area",
        tracking=True
    )
    requested_by_id = fields.Many2one(
        "res.users",
        string="Requested By",
        tracking=True,
        required=True,
        default=lambda self: self.env.user,
        help="The user who requested this project.",
    )
    amount_assigned = fields.Float(
        string="Amount Assigned",
        tracking=True,
        help="The amount of resources assigned to this project.",
    )
    amount_used = fields.Float(
        string="Amount Used",
        tracking=True,
        help="The amount of resources used in this project.",
    )
    delay_days = fields.Integer(
        string="Delay Days",
        tracking=True,
        store=True,
        compute="_compute_deviation",
        help="The number of days this project is delayed.",
    )
    deviation = fields.Float(
        string="Deviation in Execution",
        tracking=True,
        compute="_compute_deviation",
        store=True,
        help="The deviation percentage of the project budget.",
    )
    project_status = fields.Selection(
        string="Project Status",
        selection=[
            ("on_time", "On Time"),
            ("on_pause", "Paused"),
            ("alert", "Alert"),
            ("delayed", "Delayed"),
        ],
        tracking=True,
        compute="_compute_deviation",
        inverse="_inverse_project_status",
        store=True,
        help="The status of the project.",
    )
    total_advance = fields.Float(
        string="Total Advance",
        tracking=True,
        compute="_compute_total_advance",
        help="The total advance payment made for this project.",
    )
    is_completed = fields.Boolean(
        string="Is Completed",
        tracking=True,
        help="Indicates whether the project is completed.",
        related="stage_id.is_completed"
    )
    closed_date = fields.Datetime(
        string="Closed Date",
        tracking=True,
        help="The date when the project was closed.",
        compute="_compute_closed_date",
    )
    stage_ids = fields.One2many(
        "project.project.stage.advance",
        "project_id",
        string="Stage Advances",
        tracking=True,
        help="The stages and their advances for this project.",
    )

    def _compute_total_advance(self):
        for project in self:
            if not project.stage_ids:
                project.total_advance = 0.0
                continue
            total = sum(stage.advance for stage in project.stage_ids)
            project.total_advance = total / len(project.stage_ids)

    @api.depends("stage_id")
    def _compute_closed_date(self):
        for project in self:
            project.closed_date = False
            if project.stage_id.is_completed:
                project.closed_date = fields.Datetime.now()

    def _inverse_project_status(self):
        for project in self:
            project.project_status = project.project_status

    @api.depends("date_start", "date", "closed_date", "resource_calendar_id")
    def _compute_deviation(self):
        """Compute delay days and deviation percentage for each project, based on working days."""
        from datetime import datetime, time
        for project in self:
            project.delay_days = 0
            project.deviation = 0.0
            project.project_status = "on_time"

            if not (project.date_start and project.date):
                continue

            # Convierte fechas a datetime
            start_dt = datetime.combine(project.date_start, time.min)
            end_dt = datetime.combine(project.date, time.max)
            ref_dt = datetime.combine(project.closed_date or fields.Date.today(), time.max)

            # Usa el calendario del proyecto o el general de la compañía
            calendar = project.resource_calendar_id or self.env.company.resource_calendar_id

            # Duración planificada en días laborales
            duration_hours = calendar.get_work_hours_count(start_dt, end_dt)
            duration_days = duration_hours / (calendar.hours_per_day or 8.0)

            # Retraso solo si ref_dt > fecha final planificada
            if ref_dt > end_dt:
                delay_hours = calendar.get_work_hours_count(end_dt, ref_dt)
                delay_days = delay_hours / (calendar.hours_per_day or 8.0)
            else:
                delay_days = 0

            project.delay_days = max(0, delay_days)
            project.deviation = (
                (project.delay_days / duration_days if duration_days else 0)
                * (100 - project.total_advance)
            )

            # Estado del proyecto según desviación
            if project.deviation < 10:
                project.project_status = "on_time"
            elif 10 <= project.deviation <= 15:
                project.project_status = "alert"
            else:
                project.project_status = "delayed"

    @api.model
    def create(self, vals):
        """ Override create method to set default values and link task types. """
        project = super(ProjectProject, self).create(vals)
        task_type_ids = self.env.ref("project_bol.project_task_type_stage_0")
        task_type_ids += self.env.ref("project_bol.project_task_type_stage_1")
        task_type_ids += self.env.ref("project_bol.project_task_type_stage_2")
        task_type_ids.sudo().write({
            "project_ids": [(4, project.id)]
        })
        project.stage_ids = [
            (0, 0, {
                "stage_id": self.env.ref("project_bol.project_project_stage_0").id,
                "project_id": project.id,
            }),
            (0, 0, {
                "stage_id": self.env.ref("project_bol.project_project_stage_1").id,
                "project_id": project.id,
            }),
            (0, 0, {
                "stage_id": self.env.ref("project_bol.project_project_stage_2").id,
                "project_id": project.id,
            }),
            (0, 0, {
                "stage_id": self.env.ref("project_bol.project_project_stage_3").id,
                "project_id": project.id,
            }),
            (0, 0, {
                "stage_id": self.env.ref("project_bol.project_project_stage_4").id,
                "project_id": project.id,
            }),
            (0, 0, {
                "stage_id": self.env.ref("project_bol.project_project_stage_5").id,
                "project_id": project.id,
            }),
        ]
        return project
