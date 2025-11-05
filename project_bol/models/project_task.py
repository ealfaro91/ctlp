
from odoo import api, fields, models


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "mail.thread", "mail.activity.mixin"]

    project_stage_id = fields.Many2one(
        "project.project.stage",
        string="Project Stage",
        tracking=True,
        help="The stage of the project this task belongs to.",
        default=lambda self: self.project_id.stage_id.id,
    )
    advance = fields.Float(
        string="Advance",
        compute="_compute_advance",
        help="The percentage of advance for this task."
    )

    @api.depends("stage_id")
    def _compute_advance(self):
        for record in self:
            record.advance = record.stage_id.weight
