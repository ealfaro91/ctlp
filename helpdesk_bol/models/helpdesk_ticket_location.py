# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicketLocation(models.Model):
    _name = "helpdesk.ticket.location"
    _description = "Helpdesk Ticket Location"
    _order = "sequence,name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(
        default=True,
        tracking=True
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10
    )
    name = fields.Char(
        string="Location",
        tracking=True,
        translate=True
    )
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        tracking=True,
        required=True,
        domain="[('has_locations', '=', True)]",
        ondelete="cascade"
    )
    is_other = fields.Boolean(
        string="Other",
        tracking=True
    )

    @api.constrains('is_other')
    def _check_unique_is_other(self):
        for record in self:
            if record.is_other:
                existing = self.search([
                    ('is_other', '=', True),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing:
                    raise ValidationError("Only one record can have 'Is Other' set to True.")

