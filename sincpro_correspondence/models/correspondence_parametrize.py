from odoo import Command, api, fields, models

TYPE_CORRESPONDENCE = [("internal", "Interno"), ("external", "Externo")]


class Actions(models.Model):
    _name = "correspondence.action"
    _description = "Acciones de correspondencia"
    _rec_name = "action"

    action = fields.Char(string="Accion", required=True)
    priority = fields.Integer(string="Prioridad", default=10)
    active = fields.Boolean(default=True)
    color = fields.Integer("Color Index")


class CorrespondenceType(models.Model):
    _name = "correspondence.type"
    _description = "Tipo de correspodencia"
    _order = "priority, id"

    name = fields.Char(string="Tipo", required=True)
    image = fields.Binary(string="Image")
    color = fields.Integer("Color Index")
    description = fields.Text(string="Descripcion")
    type = fields.Selection(
        TYPE_CORRESPONDENCE, string="Tipo", required=True, default="internal"
    )
    priority = fields.Integer(string="Prioridad", default=10)
    sequence_id = fields.Many2one("ir.sequence", "Reference Sequence", copy=False)
    prefix = fields.Char(string="Codigo/Prefijo", copy=False, required=True)
    suffix = fields.Char(string="Sufijo", copy=False)
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Create a sequence for each type of correspondence
        """
        for vals in vals_list:
            constructor_dict = {
                "name": f"Sequence", # {vals['name']} {vals['prefix']}
                "padding": 5,
                "prefix": "%(year)s/", # f"{vals['prefix']}/%(year)s/",
                "use_date_range": True,
            }

            if vals.get("suffix"):
                constructor_dict["suffix"] = vals["suffix"]

            # Add restart number during 30 years, if still the company exists
            constructor_dict["date_range_ids"] = [
                Command.create(
                    {
                        "number_next_actual": 1,
                        "date_from": f"{year}-01-01",
                        "date_to": f"{year}-12-31",
                    }
                )
                for year in range(2024, 2054)
            ]

            sequence = self.env["ir.sequence"].create(constructor_dict)

            vals["sequence_id"] = sequence.id
        return super().create(vals_list)
