# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AlertType(models.Model):
    _name = "alert.type"
    _description = "Ocupación del cliente"

    code = fields.Char(string="Código")
    name = fields.Char(string="Tipo de Alerta")

