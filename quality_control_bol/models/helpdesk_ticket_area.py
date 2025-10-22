# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicketArea(models.Model):
    _inherit = "helpdesk.ticket.area"

    show_in_directory = fields.Boolean(
        string="Show in Directories",
        default=False,
        tracking=True,
        help="If checked, this area will be displayed in the directories."
    )
