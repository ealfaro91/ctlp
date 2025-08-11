from odoo import api, fields, models


class ProjectTaskType(models.Model):
    _name = "project.task.type"
    _inherit = ["project.task.type", "mail.thread", "mail.activity.mixin"]

    weight = fields.Integer(
        string="Weight", default=0,
        required=True,
        help="Weight of the task in percentage (0-100)"
    )
    is_completed = fields.Boolean(
        string="Completed",
        default=False, help="Indicates if the task is completed"
    )
