# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_location = fields.Boolean(
        string="Es una Ubicación",
    )
    street = fields.Char(string="Calle")
    colonia = fields.Char(string="Colonia")
    postal_code = fields.Char(string="Código postal")
    m2 = fields.Char(string="Metros Cuadrados Terreno")
    mc = fields.Char(string="Metros Cuadrados Construcción")
    outdoor_number = fields.Char(string="Número exterior")
    interior_number = fields.Char(string="Número interior")
    property_type = fields.Selection(
        [],
        String="Tipo de inmueble"
    )