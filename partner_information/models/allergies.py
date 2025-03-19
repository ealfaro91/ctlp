
from odoo import models, fields


class Allergies(models.Model):
    _name = 'allergies'
    _description = 'Allergies'
    sql_constraints = [('name_uniq', 'unique (name)', 'The name must be unique!')]

    name = fields.Char(string='Name', required=True)
