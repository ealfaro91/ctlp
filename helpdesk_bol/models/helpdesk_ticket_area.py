# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicketArea(models.Model):
    _name = "helpdesk.ticket.area"
    _description = "Helpdesk Ticket Area"
    _order = "sequence,name"
    _inherit = ["mail.thread", "mail.activity.mixin",]
    _sql_constraints = [("code_uniq", "unique(code)",  "Area code must be unique",)]

    active = fields.Boolean(default=True, tracking=True)
    sequence = fields.Integer(
        string="Sequence",
        default=10
    )
    name = fields.Char(
        string="Area", tracking=True,
        translate=True,
        required=True
    )
    code = fields.Char(
        string="Code",
        tracking=True,
        required=True
    )
    type_ids = fields.One2many(
        "helpdesk.ticket.type",
        "area_id",
        string="Types",
        tracking=True
    )
    has_categories = fields.Boolean(
        string="Has Categories",
        default=True,
        tracking=True,
        help="Display categories in the helpdesk ticket form view."
    )
    has_locations = fields.Boolean(
        string="Has Locations",
        default=False,
        tracking=True,
        help="Display locations in the helpdesk ticket form view."
    )
    has_origins = fields.Boolean(
        string="Has Origins",
        default=False,
        tracking=True,
        help="Display origins in the helpdesk ticket form view."
    )
    color = fields.Integer(string="Color Index", default=0, tracking=True)
    description = fields.Text(
        string="Description",
        tracking=True,
        help="This text will be displayed in the helpdesk ticket form view."
    )
    show_in_external_portal = fields.Boolean(
        string="Show in External Portal",
        default=False,
        tracking=True,
        help="If checked, this area will be displayed in the external portal for SDSS."
             " This means this area is for external customers"
    )
    sequence_id = fields.Many2one(
        "ir.sequence",
        string="Sequence",
        required=True,
        tracking=True,
        domain="[('code', 'in', ('helpdesk.ticket.sdss.sequence', 'helpdesk.ticket.sequence'))]",
        help="This is the sequence that will be used to generate the ticket number."
    )
    ticket_ids = fields.One2many(
        "helpdesk.ticket",
        "area_id",
        string="Tickets",
        tracking=True
    )
    ticket_count = fields.Integer(
        string="Tickets",
        compute="_compute_ticket_count",
        store=True
    )
    mail_server_id = fields.Many2one(
        "ir.mail_server",
        string="Mail Server",
        required=True,
        tracking=True,
        help="This is the mail server that will be used to send emails."
    )
    default_reopen_area = fields.Boolean(
        string="Default Reopen Area",
        default=False,
        tracking=True,
        help="If checked, this area will be used as the default area when reopening a ticket."
    )

    def _compute_ticket_count(self):
        for area in self:
            area.ticket_count = len(area.ticket_ids)

    def action_view_tickets(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Tickets",
            "res_model": "helpdesk.ticket",
            "view_mode": "tree,form",
            "domain": [("area_id", "=", self.id)],
            "context": {"create": False},
        }

    @api.constrains('default_reopen_area')
    def _check_unique_is_other(self):
        for record in self:
            if record.default_reopen_area:
                existing = self.search([
                    ('default_reopen_area', '=', True),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing:
                    raise ValidationError("Only one record can have 'Is Other' set to True.")


