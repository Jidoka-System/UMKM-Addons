import time
from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, AccessDenied
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class GeneralViewInherit(models.TransientModel):
    _inherit = 'account.general.ledger'

    # override
    def _get_report_values(self, data):
        docs = data['model']
        display_account = data['display_account']
        init_balance = False
        journals = data['journals']
        accounts = self.env['account.account'].search([])
        if not accounts:
            raise UserError(_("No Accounts Found! Please Add One"))
        account_res = self._get_accounts(accounts, init_balance, display_account, data)
        debit_total = 0
        debit_total = sum(x['debit'] for x in account_res)
        credit_total = sum(x['credit'] for x in account_res)
        debit_balance = round(debit_total,2) - round(credit_total,2)
        return {
            'doc_ids': self.ids,
            'debit_total': debit_total,
            'credit_total': credit_total,
            'debit_balance':debit_balance,
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }
    