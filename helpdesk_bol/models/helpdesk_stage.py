# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskStage(models.Model):
    _inherit = "helpdesk.stage"

    active = fields.Boolean(default=True)
    survey_id = fields.Many2one(
        "survey.survey",
        string="Invitación a encuesta"
    )

    is_solved = fields.Boolean(string="Esta resuelto?")
    is_process = fields.Boolean(string="Esta en proceso?")
