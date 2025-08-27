
from odoo import fields, models, api, _


class ProjectProject(models.Model):
    _inherit = "project.project"

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
        required=True,
        help="The area responsible for executing this project.",
    )
    product_owner_id = fields.Many2one(
        "res.users",
        string="Product Owner",
        tracking=True,
        required=True,
        help="The user who is the product owner for this project.",
    )
    product_manager_id = fields.Many2one(
        "res.users",
        string="Product Manager",
        tracking=True,
        required=True,
        help="The user who is the product manager for this project.",
    )
    requested_area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Requested Area",
        tracking=True,
        required=True,
        help="The area that requested this project.",
    )
    requested_area = fields.Char()
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
        compute="_compute_deviation",
        help="The number of days this project is delayed.",
    )
    deviation = fields.Float(
        string="Deviation in Execution",
        tracking=True,
        compute="_compute_deviation",
        help="The deviation percentage of the project budget.",
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
        #related="stage_id.is_completed"
    )
    closed_date = fields.Datetime(
        string="Closed Date",
        tracking=True,
        help="The date when the project was closed."
    )
    stage_ids = fields.One2many(
        "project.project.stage.advance",
        "project_id",
        string="Stage Advances",
        tracking=True,
        help="The stages and their advances for this project.",
    )

    def _compute_total_advance(self):
        """ REVISAR """
        for project in self:
            tasks = project.task_ids
            if not tasks:
                project.total_advance = 0.0
                continue
                # Sumamos los weights de las etapas de todas las tareas
                total_weight = sum(task.stage_id.weight for task in tasks)
                # Weight máximo de etapas en el proyecto (opcional)
                max_weight = max(project.stage_ids.mapped('weight')) or 1
                # Avance como porcentaje
                project.progress = (total_weight / (len(tasks) * max_weight)) * 100
            project.total_advance = 0.0

    def _compute_deviation(self):
        """ Compute delay days and deviation percentage for each project. """
        for project in self:
            project.delay_days = 0
            project.deviation = 0.0
            if project.date:
                if project.closed_date:
                    delay = (project.closed_date.date() - project.date).days
                    project.delay_days = max(0, delay)

                    # calcular duración original
                    if project.start_date:
                        duration = (project.date - project.date_start.date()).days or 1
                        project.deviation = (project.delay_days / duration) * 100

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
    #    project_project_stage_0
        return project
