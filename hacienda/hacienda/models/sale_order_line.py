# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "sale.order.line"
    
    # @api.onchange("company_id")
    # def onchange_company_id(self):
    #     for rec in self:
    #         return {"domain": {"product_id": [("type", "=", "service")]}}