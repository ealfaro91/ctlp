# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PartnerOccupation(models.Model):
    _name = "partner.occupation"
    _description = "Ocupación del partner"

    code = fields.Char(string="Código")
    name = fields.Char(string="Ocupación")

