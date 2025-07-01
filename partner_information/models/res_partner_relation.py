from odoo import models, fields


class ResPartnerRelation(models.Model):
    _name = 'res.partner.relation'
    _description = 'Partner Relation'
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name must be unique!'),
    ]

    name = fields.Char(string='Name', required=True)
