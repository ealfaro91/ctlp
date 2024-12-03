from odoo import models, fields


class PreferredSubstance(models.Model):
    _name = 'preferred.substance'
    _description = 'Preferred Substance'
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name must be unique!'),
    ]

    name = fields.Char(string='Name', required=True)
