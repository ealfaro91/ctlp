# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sequence = fields.Char(string='Sequence')

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        res._assign_product_sequence()
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        self._assign_product_sequence()
        return res

    def _assign_product_sequence(self):
        for product in self:
            category_id = self.env['product.category.sequence'].search([
                ('category_id', '=', product.categ_id.id)], limit=1)
            if category_id:
                product.sequence = category_id.sequence_id.next_by_id()
