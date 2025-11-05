from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
        compute="_compute_advance",
        help="The percentage of advance for this stage.",
    )

    def _compute_advance(self):
        """ Compute the advance for this project stage. """
        for rec in self:
            rec.advance = 0.0
            tasks = rec.project_id.task_ids.filtered(
                lambda t: t.project_stage_id == rec.stage_id
            )
            if len(tasks) == 0:
                continue
            total_task_weight = sum(task.stage_id.weight for task in tasks)
            rec.advance = total_task_weight / len(tasks)






