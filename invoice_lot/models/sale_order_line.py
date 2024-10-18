from odoo import models, fields, api
from collections import defaultdict

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one('stock.lot', string='Lot')
    lot_quantity = fields.Float(string='Lot Quantity')
    lot_expiration_date = fields.Date(string='Lot Expiration Date')


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.env.user.has_group('stock.group_production_lot'):
            lot = self._get_lot_expiring_soon(self.product_id)
            if lot:
                self.lot_id = lot.id
                self.lot_quantity = lot.product_qty
                self.lot_expiration_date = lot.expiration_date

    @api.model
    def _get_lot_expiring_soon(self, product_id):
        stock_lot = self.env['stock.lot'].search([
            ('product_id', '=', product_id.id),
            ('product_qty', '>', 0),
            ('expiration_date', '>=', fields.Datetime.now())
        ], order='expiration_date asc', limit=1)
        return stock_lot
