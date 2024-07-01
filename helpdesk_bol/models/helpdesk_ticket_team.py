# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    area_type = fields.Selection([('TI', 'TI')], string="Area", tracking=True)



