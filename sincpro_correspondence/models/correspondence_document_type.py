from odoo import api, fields, models


class CorrespondenceDocumentType(models.Model):
    _name = "correspondence.document.type"
    _description = "Tipo de documento"

    name = fields.Char(string="Tipo de documento", required=True)
    sequence = fields.Integer(string="Prioridad", default=10)
    active = fields.Boolean(default=True)
    color = fields.Integer("Color Index")
