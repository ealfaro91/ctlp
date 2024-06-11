from odoo import fields, models


class HelpdeskCategory(models.Model):
    _name = "helpdesk.ticket.category"
    _description = "Helpdesk Ticket Category"
    _order = "sequence, id"
    _inherit = ["mail.thread", "mail.activity.mixin",]


    sequence = fields.Integer(default=10, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(
        string="Category",
        required=True,
        translate=True,
        tracking=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        tracking=True
    )
