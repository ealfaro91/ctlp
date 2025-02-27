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
                sequence = product.sequence_id

                # Check for existing sequences for the same product and customer
                customer_existing_lines = self.env['sale.order.line'].search([
                    ('product_id', '=', product.id),
                    ('order_id.partner_id', '=', customer.id),
                    ('product_sequence', '!=', False),
                ])

                if customer_existing_lines:
                    if not product.repeateance_prefix:
                        raise ValidationError(_('Product %s has repeatance sequences but no repeatance prefix defined.') % product.name)
                    # If the product is repeated for the same customer, assign a prefixed sequence
                    prefix = product.repeateance_prefix
                    line.product_sequence = f"{prefix}-{sequence.next_by_id()}"
                else:
                    # Assign a simple global sequence without a prefix
                    line.product_sequence = f"{sequence.next_by_id()}"
                order.product_sequences = ', '.join(order.order_line.mapped('product_sequence'))
        return res
