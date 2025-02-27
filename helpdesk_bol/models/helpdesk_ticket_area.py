# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskTicketArea(models.Model):
    _name = "helpdesk.ticket.area"
    _description = "Helpdesk Ticket Area"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin",]
    _sql_constraints = [("code_uniq", "unique(code)",  "Area code must be unique",)]

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Area", tracking=True, translate=True)
    code = fields.Char(string="Code", tracking=True)
    type_ids = fields.One2many("helpdesk.ticket.type", "area_id", string="Types", tracking=True)
    color = fields.Integer(string="Color Index", default=0, tracking=True)
    description = fields.Text(
        string="Descripción",
        tracking=True,
        help="This text will be displayed in the helpdesk ticket form view."
    )
    show_in_external_portal = fields.Boolean(
        string="Show in External Portal",
        default=False,
        tracking=True,
        help="If checked, this area will be displayed in the external portal."
    )
    sequence_id = fields.Many2one(
        "ir.sequence",
        string="Sequence",
        tracking=True
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
    mail_template_ids = fields.Many2many(
        "mail.template",
        string="Email Templates",
        tracking=True
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

