from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    time_to_close_ticket = fields.Float(
        string="Automatic ticket closure time (hours)",
        default=48
    )
    login_from_ws = fields.Boolean(
        string="Allow login from web service",
    )
    validate_payment_from_ws = fields.Boolean(
        string="Allow login from web service",
        default=False
    )
    ws_url = fields.Char(
        string="Web service URL",
        default="https://odootest.ctlp.bo/jsonrpc"
    )
    payment_ws = fields.Char(
        string="Payment Web service URL",
        default="https://odootest.ctlp.bo/jsonrpc"
    )
    payment_delayed_message = fields.Text(
        string="Payment delayed message"
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('helpdesk_bol.time_to_close_ticket', self.time_to_close_ticket)
        self.env['ir.config_parameter'].set_param('helpdesk_bol.login_from_ws', self.login_from_ws)
        self.env['ir.config_parameter'].set_param('helpdesk_bol.ws_url', self.ws_url)
        self.env['ir.config_parameter'].set_param('helpdesk_bol.payment_ws', self.payment_ws)
        self.env['ir.config_parameter'].set_param('helpdesk_bol.validate_payment_from_ws', self.validate_payment_from_ws)
        self.env['ir.config_parameter'].set_param('helpdesk_bol.payment_delayed_message', self.payment_delayed_message)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['time_to_close_ticket'] = float(
            self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.time_to_close_ticket')
        )
        res['login_from_ws'] = self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.login_from_ws')
        res['ws_url'] = self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.ws_url')
        res['payment_ws'] = self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.payment_ws')
        res['validate_payment_from_ws'] = self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.validate_payment_from_ws')
        res['payment_delayed_message'] = self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.payment_delayed_message')
        return res




