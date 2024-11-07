# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _name = "res.users"
    _inherit = ["res.users", "mail.thread", "mail.activity.mixin"]

    area = fields.Char(
        string="Area Active Directory",
        help="Area Active Directory",
        tracking=True
    )
    area_ids = fields.Many2many(
        "helpdesk.ticket.area",
        string="Access Areas",
        compute="_compute_area_ids"
    )

    def _compute_area_ids(self):
        for user in self:
            area_ids = self.env['helpdesk.ticket.team'].search([('user_ids', 'in', user.id)]).mapped('area_id')
            user.area_ids = [(6, 0, area_ids.ids)]


