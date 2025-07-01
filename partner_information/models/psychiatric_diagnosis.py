
from odoo import models, fields


class PsychiatricDiagnosis(models.Model):
    _name = 'psychiatric.diagnosis'
    _description = 'Psychiatric Diagnosis'
    sql_constraints = [('name_uniq', 'unique (name)', 'The name must be unique!')]

    name = fields.Char(string='Name', required=True)
