# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_sequences = fields.Char(string="Product Sequence")

    def action_confirm(self):
        """Override the confirm action to assign product sequences."""
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            for line in order.order_line:
                # Ensure the line has a product
                if not line.product_id:
                    continue

                # Get the customer and product information
                customer = order.partner_id
                product = line.product_id

                # Calculate the global sequence for this product across all sale order lines
                global_existing_lines = self.env['sale.order.line'].search([
                    ('product_id', '=', product.id),
                    ('product_sequence', '!=', False),
                ])
                global_sequence = len(global_existing_lines) + 1

                # Check for existing sequences for the same product and customer
                customer_existing_lines = self.env['sale.order.line'].search([
                    ('product_id', '=', product.id),
                    ('order_id.partner_id', '=', customer.id),
                    ('product_sequence', '!=', False),
                ])

                if customer_existing_lines:
                    if not product.repeatenance_prefix:
                        raise ValidationError(_('Product %s has repeatance sequences but no repeatance prefix defined.') % product.name)
                    # If the product is repeated for the same customer, assign a prefixed sequence
                    prefix = product.repeatenance_prefix
                    line.product_sequence = f"{prefix}-{global_sequence}"
                else:
                    # Assign a simple global sequence without a prefix
                    line.product_sequence = f"{global_sequence}"
                order.product_sequences = ', '.join(order.order_line.mapped('product_sequence'))
        return res
