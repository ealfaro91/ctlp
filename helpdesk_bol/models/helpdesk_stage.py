# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskStage(models.Model):
    _inherit = "helpdesk.stage"

    active = fields.Boolean(default=True, tracking=True)
    survey_id = fields.Many2one(
        "survey.survey",
        string="Invitación a encuesta",
        tracking=True
    )

    is_solved = fields.Boolean(string="Esta resuelto?", tracking=True)
    is_process = fields.Boolean(string="Esta en proceso?", tracking=True)
