
from odoo import models, fields


class AxisCatalog(models.Model):
    _name = 'axis.catalog'
    _description = 'Axis catalog'
    sql_constraints = [('name_type_uniq', 'unique(name, axis_type)', 'The name and axis type must be unique')]


    name = fields.Char(string='Name', required=True)
    axis_type = fields.Selection([
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4")
    ], string='Axis Type', required=True, default="1")
