from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        related='pos_config_id.analytic_account_id',
        readonly=False,
    )
    pos_analytic_all_lines = fields.Boolean(
        related='pos_config_id.analytic_all_lines',
        readonly=False,
    )
