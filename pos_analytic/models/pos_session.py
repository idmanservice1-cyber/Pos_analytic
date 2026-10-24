from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _with_pos_analytic(self):
        ctx = self.config_id._get_pos_analytic_context()
        return self.with_context(**ctx) if ctx else self

    def _validate_session(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        # Covers the closing entry, bank payments, cash statement lines, cash
        # differences, end-of-session pickings and their stock valuation entries.
        return super(PosSession, self._with_pos_analytic())._validate_session(
            balancing_account, amount_to_balance, bank_payment_method_diffs)

    def try_cash_in_out(self, _type, amount, reason, partner_id, extras):
        return super(PosSession, self._with_pos_analytic()).try_cash_in_out(
            _type, amount, reason, partner_id, extras)
