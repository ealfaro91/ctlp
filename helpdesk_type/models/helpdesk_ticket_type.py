# Copyright (C) 2019 Konos
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models, Command


class HelpdeskType(models.Model):
    """Helpdesk Type"""

    _name = "helpdesk.ticket.type"
    _description = "Helpdesk Ticket Type"
    _order = "name asc"
    _inherit = ["mail.thread", "mail.activity.mixin"]


    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string="Name", required=True, tracking=True, translate=True)
    team_ids = fields.Many2many(
        "helpdesk.ticket.team",
        string="Teams",
        help="Helpdesk teams allowed to use this type.",
        tracking=True
    )

    def _mail_track(self, tracked_fields, initial_values):
        changes, tracking_value_ids = super()._mail_track(tracked_fields, initial_values)
        # Many2many tracking
        if len(changes) > len(tracking_value_ids):
            for changed_field in changes:
                if tracked_fields[changed_field]['type'] in ['one2many', 'many2many']:
                    field = self.env['ir.model.fields']._get(self._name, changed_field)
                    vals = {
                        'field': field.id,
                        'field_desc': field.field_description,
                        'field_type': field.ttype,
                        'tracking_sequence': field.tracking,
                        'old_value_char': ', '.join(initial_values[changed_field].mapped('name')),
                        'new_value_char': ', '.join(self[changed_field].mapped('name')),
                    }
                    tracking_value_ids.append(Command.create(vals))
        return changes, tracking_value_ids
