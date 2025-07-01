from odoo import models, fields


class ResPartnerStatus(models.Model):
    _name = 'res.partner.status'
    _description = 'Partner Status'
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name must be unique!'),
    ]

    name = fields.Char(string='Name', required=True)
