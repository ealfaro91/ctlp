
from odoo import models, fields, api


class ProjectFsnSystem(models.Model):
    _name = "project.fsn.system"
    _description = "Project FSN System"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="System Name",
        required=True,
        tracking=True,
        help="The name of the system related to this FSN.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
        help="Indicates whether this system is currently active.",
    )
