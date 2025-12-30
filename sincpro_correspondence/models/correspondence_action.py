from odoo import Command, api, fields, models



class CorrespondenceAction(models.Model):
    _name = "correspondence.action"
    _description = "Acciones de correspondencia"
    _rec_name = "action"

    action = fields.Char(string="Accion", required=True)
    priority = fields.Integer(string="Prioridad", default=10)
    active = fields.Boolean(default=True)
    color = fields.Integer("Color Index")
