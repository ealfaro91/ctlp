
from odoo import models, fields, api


class ProjectFsnBenefit(models.Model):
    _name = "project.fsn.benefit"
    _description = "Project FSN Benefit"
    _inherit = ["mail.thread", "mail.activity.mixin"]


    name = fields.Char(
        string="Benefit Name",
        required=True,
        tracking=True,
        help="The name of the benefit related to this FSN.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
        help="Indicates whether this benefit is currently active.",
    )
    color = fields.Integer(
        string="Color",
        default=0,
        tracking=True,
        help="Color code for the benefit, used for categorization.",
    )
