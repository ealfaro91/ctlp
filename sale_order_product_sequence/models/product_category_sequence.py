

# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductCategorySequence(models.Model):
    _name = 'product.category.sequence'
    _description = 'Product Category Sequence'
    _sql_constraints = [
        ('category_id_uniq', 'unique(category_id)', 'Category must be unique!'),
    ]

    def name_get(self):
        """Get the proper display name formatted as 'ZIP, name, state, country'."""
        res = []
        for rec in self:
            name = "{0} - {1}".format(
                rec.sequence_id.prefix, rec.category_id.name)
            res.append(name)
        return res

    category_id = fields.Many2one('product.category', string='Category', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence', required=True)
