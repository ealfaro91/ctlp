# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HelpdeskStage(models.Model):
    _inherit = "helpdesk.stage"

    active = fields.Boolean(default=True, tracking=True)

