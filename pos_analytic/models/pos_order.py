from odoo import models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _with_pos_analytic(self):
        ctx = self[:1].config_id._get_pos_analytic_context()
        return self.with_context(**ctx) if ctx else self

    def _generate_pos_order_invoice(self):
        # Covers the customer invoice/refund, its payment entries and the
        # reversal of the closing entry for orders invoiced after closing.
        return super(PosOrder, self._with_pos_analytic())._generate_pos_order_invoice()

    def _create_order_picking(self):
        # Covers real-time stock valuation entries created by the picking.
        return super(PosOrder, self._with_pos_analytic())._create_order_picking()
