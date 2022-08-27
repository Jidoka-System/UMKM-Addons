from odoo import models, fields


class AccountFinancialReportInherit(models.Model):
    _inherit = 'account.financial.report'

    type = fields.Selection(
        selection_add=[('total', 'Total')], ondelete={'total': 'cascade'})
    is_no_children = fields.Boolean(string='Is no children', default=False)
