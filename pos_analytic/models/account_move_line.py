from odoo import api, models

PL_GROUPS = ('income', 'expense')
SKIPPED_DISPLAY_TYPES = ('line_section', 'line_note', 'line_subsection')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        analytic_account = self._get_pos_analytic_account()
        if not analytic_account:
            return super().create(vals_list)

        all_lines = self.env.context.get('pos_analytic_all_lines')
        Account = self.env['account.account']

        # 1. Lines whose account is already known: set the distribution in the vals
        #    so no extra write is needed (closing entry, payments, statements, ...).
        for vals in vals_list:
            if vals.get('display_type') in SKIPPED_DISPLAY_TYPES or not vals.get('account_id'):
                continue
            account = Account.browse(vals['account_id'])
            if all_lines or account.internal_group in PL_GROUPS:
                vals['analytic_distribution'] = self._pos_analytic_merge(
                    vals.get('analytic_distribution'), analytic_account)

        lines = super().create(vals_list)

        # 2. Lines whose account was computed after creation (e.g. invoice lines
        #    created from a product): tag them now.
        for line in lines:
            if line.display_type in SKIPPED_DISPLAY_TYPES:
                continue
            if not (all_lines or line.account_id.internal_group in PL_GROUPS):
                continue
            if self._pos_analytic_has_plan(line.analytic_distribution, analytic_account):
                continue
            line.analytic_distribution = self._pos_analytic_merge(
                line.analytic_distribution, analytic_account)
        return lines

    @api.model
    def _get_pos_analytic_account(self):
        account_id = self.env.context.get('pos_analytic_account_id')
        if not account_id:
            return self.env['account.analytic.account']
        return self.env['account.analytic.account'].browse(account_id).exists()

    @api.model
    def _pos_analytic_has_plan(self, distribution, analytic_account):
        """True if ``distribution`` already contains an account of the same root plan
        as ``analytic_account`` (adding ours would exceed 100% on that plan)."""
        if not distribution:
            return False
        root_plan = analytic_account.root_plan_id
        account_ids = {
            int(aid) for key in distribution for aid in str(key).split(',') if aid.strip().isdigit()
        }
        existing = self.env['account.analytic.account'].browse(list(account_ids)).exists()
        return any(acc.root_plan_id == root_plan for acc in existing)

    @api.model
    def _pos_analytic_merge(self, distribution, analytic_account):
        """Return ``distribution`` with the POS analytic account added at 100%.

        An existing distribution on another plan (e.g. coming from a sale order or
        a distribution model) is kept; an existing distribution on the same plan
        wins and is left untouched.
        """
        distribution = dict(distribution or {})
        if self._pos_analytic_has_plan(distribution, analytic_account):
            return distribution
        distribution[str(analytic_account.id)] = 100
        return distribution
