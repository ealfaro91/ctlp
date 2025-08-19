from odoo import api, fields, models


class ProjectProjectStage(models.Model):
    _name = "project.project.stage"
    _inherit = ["project.project.stage", "mail.thread", "mail.activity.mixin"]

    weight = fields.Integer(
        string="Weight", default=0,
        required=True,
        tracking=True,
        help="Weight of the task in percentage (0-100)"
    )
    is_completed = fields.Boolean(
        string="Completed",
        default=False, help="Indicates if the task is completed",
        tracking=True,
    )


