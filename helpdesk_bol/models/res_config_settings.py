from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    time_to_close_ticket = fields.Float(
        string="Automatic ticket closure time (hours)",
        default=48,
        config_parameter='helpdesk_bol.time_to_close_ticket',
    )
    login_from_ws = fields.Boolean(
        string="Allow login from web service",
        config_parameter='helpdesk_bol.login_from_ws'
    )
    validate_payment_from_ws = fields.Boolean(
        string="Allow login from web service",
        default=False
    )
    ws_url = fields.Char(
        string="Web service URL",
        default="https://odootest.ctlp.bo/jsonrpc",
        config_parameter='helpdesk_bol.ws_url'
    )
    payment_ws = fields.Char(
        string="Payment Web service URL",
        default="https://odootest.ctlp.bo/jsonrpc",
        config_parameter='helpdesk_bol.payment_ws'
    )
    payment_delayed_message = fields.Char(
        string="Payment delayed message",
        config_parameter='helpdesk_bol.payment_delayed_message'
    )
    password_lifetime = fields.Integer(
        string='Password Lifetime (days)',
        config_parameter='helpdesk_bol.password_lifetime',
    )
    forced_password_change = fields.Boolean(
        string='Redirect to Change Password',
        config_parameter='helpdesk_bol.forced_password_change',
    )
    success_message = fields.Char(
        string="Success message",
        config_parameter='helpdesk_bol.success_message',
        default="Thank you for sharing your concern with us. We are working on your request, "
                "and you will soon receive an email with the follow-up to your ticket."
                " We also recommend checking your spam folder."

    )

    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     self.env['ir.config_parameter'].set_param(, self.time_to_close_ticket)
    #     self.env['ir.config_parameter'].set_param(, self.login_from_ws)
    #     self.env['ir.config_parameter'].set_param('helpdesk_bol.ws_url', self.ws_url)
    #     self.env['ir.config_parameter'].set_param('helpdesk_bol.payment_ws', self.payment_ws)
    #     self.env['ir.config_parameter'].set_param('helpdesk_bol.validate_payment_from_ws', self.validate_payment_from_ws)
    #     self.env['ir.config_parameter'].set_param('helpdesk_bol.payment_delayed_message', self.payment_delayed_message)

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




