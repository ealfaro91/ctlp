from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    time_to_close_ticket = fields.Float(
        string="Automatic ticket closure time (hours)",
        default=48
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('helpdesk_bol.time_to_close_ticket', self.time_to_close_ticket)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['time_to_close_ticket'] = float(
            self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.time_to_close_ticket')
        )
        return res


