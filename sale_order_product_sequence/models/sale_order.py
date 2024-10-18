# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_sequences = fields.Char(string="Product Sequence", compute='_compute_product_sequences', store=True)

    @api.depends('order_line.product_id')
    def _compute_product_sequences(self):
        for order in self:
            sequences = order.order_line.mapped('product_id.sequence')
            order.product_sequences = ', '.join(sequences)
