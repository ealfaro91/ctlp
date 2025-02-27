# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    repeateance_prefix = fields.Char(string='Repeatance Prefix')
    sequence_id = fields.Many2one(
        'ir.sequence', string='Sequence',
    )


