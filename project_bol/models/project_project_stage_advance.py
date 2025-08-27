from odoo import api, fields, models


class ProjectProjectStageAdvance(models.Model):
    _name = "project.project.stage.advance"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        tracking=True,
        help="The project associated with this stage advance.",
    )
    stage_id = fields.Many2one(
        "project.project.stage",
        string="Stage",
        required=True,
        tracking=True,
        help="The stage associated with this advance.",
    )
    advance = fields.Float(
        string="Advance (%)",
        required=True,
        compute="_compute_advance",
        help="The percentage of advance for this stage.",
    )


    def _compute_advance(self):
        for record in self:
            record.advance = 0.0
            # Obtener tareas de esta etapa
            tasks = record.project_id.task_ids.filtered(lambda t: t.stage_id == record.stage_id)

            if len(tasks) == 0:
                continue

            # Sumar los weights de las tareas
            total_task_weight = sum(task.stage_id.weight for task in tasks)

            # Promedio por número de tareas
            record.advance = total_task_weight / len(tasks)






