
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    fsn_id = fields.Many2one(
        "project.fsn",
        string="Functional Specification Note",
        tracking=True,
        help="The Functional Specification Note related to this project.",
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
        compute="_compute_delay_days",
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
        default=100,
        help="The total advance payment made for this project.",
    )

    def _compute_deviation(self):
        for project in self:
            project.deviation = 0.0

    def _compute_delay_days(self):
        for project in self:
            project.delay_days = 0
            # if project.date_start and project.end_date:
            #     delay = (project.end_date - project.date_start).days
            #     project.delay_days = max(0, delay)
