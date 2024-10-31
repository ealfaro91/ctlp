# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def button_print_certificate(self):
        return self.env.ref("hacienda.report_sale_order").report_action(self)
