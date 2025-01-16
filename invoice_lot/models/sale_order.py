

from odoo import models, fields, api
from odoo.tools import float_compare, float_is_zero


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_invoiceable_lines(self, final=False):
        date_from = self.env.context.get('invoiceable_date_from', fields.Date.today())
        res = super()._get_invoiceable_lines(final=final)
        res = res.filtered(
            lambda l: l.recurring_invoice or l.order_id.subscription_state == '7_upsell'
            if l.order_id.is_rental_order else not l.recurring_invoice or l.order_id.subscription_state == '7_upsell')
        automatic_invoice = self.env.context.get('recurring_automatic')

        invoiceable_line_ids = []
        downpayment_line_ids = []
        pending_section = None
        for line in self.order_line:
            if line.display_type == 'line_section':
                # Only add section if one of its lines is invoiceable
                pending_section = line
                continue

            if line.state != 'sale':
                continue

            if automatic_invoice:
                # We don't invoice line before their SO's next_invoice_date
                line_condition = line.order_id.next_invoice_date and line.order_id.next_invoice_date <= date_from and line.order_id.start_date and line.order_id.start_date <= date_from
            else:
                # We don't invoice line past their SO's end_date
                line_condition = not line.order_id.end_date or (
                        line.order_id.next_invoice_date and line.order_id.next_invoice_date < line.order_id.end_date)

            line_to_invoice = False
            if line in res:
                # Line was already marked as to be invoiced
                line_to_invoice = True
            elif line.order_id.subscription_state == '7_upsell':
                # Super() already select everything that is needed for upsells
                line_to_invoice = False
            elif line.display_type or not line.recurring_invoice:
                # Avoid invoicing section/notes or lines starting in the future or not starting at all
                line_to_invoice = False
            elif line_condition:
                if (
                    line.product_id.invoice_policy == 'order'
                    and line.order_id.subscription_state != '5_renewed'
                ):
                    # Invoice due lines
                    line_to_invoice = True
                elif (
                    line.product_id.invoice_policy == 'delivery'
                    and not float_is_zero(
                    line.qty_delivered,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                ):
                    line_to_invoice = True

            if line_to_invoice:
                if line.is_downpayment:
                    # downpayment line must be kept at the end in its dedicated section
                    downpayment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = False
                invoiceable_line_ids.append(line.id)

        return self.env["sale.order.line"].browse(invoiceable_line_ids + downpayment_line_ids)
