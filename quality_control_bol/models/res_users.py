# -*- coding:  utf-8 -*-

from odoo import models, fields, api


class Users(models.Model):
    _inherit = "res.users"

    sign_signature = fields.Binary(string="Digital Signature", groups=False)
    sign_initials = fields.Binary(string="Digitial Initials", groups=False)
