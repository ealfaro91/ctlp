# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_sequence = fields.Char(string="Product Sequence", readonly=True, copy=False)

