# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    grantor_id = fields.Many2one(
        "res.users",
        string="Otorgante"
    )
