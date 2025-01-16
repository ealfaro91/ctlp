# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    repeatenance_prefix = fields.Char(string='Repeatance Prefix')


