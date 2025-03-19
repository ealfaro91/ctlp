# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    area = fields.Char(string="Area", tracking=True)
    member_code = fields.Char(string="Member Code", tracking=True)
    is_member = fields.Boolean(string="Is Member", tracking=True)
    member_code = fields.Char(
        string="Member Code",
        help="Member code from Odoo v13",
        tracking=True
    )
    payment_on_day = fields.Boolean(
        string="Payment on Day",
        help="Payment on day",
        tracking=True
    )
