# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()
        if self.env.context.get('active_model') == 'stock.picking':
            picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
            data['picking'] = picking.name
        return xml_id, data


