# -*- coding: utf-8 -*-
{
    'name': "Jidoka Dynamic Accounts Report",

    'summary': """
        Jidoka Dynamic Accounts Report""",

    'description': """
        Jidoka Dynamic Accounts Report, modifikasi addon `dynamic_accounts_report`
    """,

    'author': "Jidoka Team",
    'website': "https://jidokasystem.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'dynamic_accounts_report',
    ],

    # always loaded
    'data': [
        'views/assets.xml',
        'reports/financial_reports.xml',
    ],
    'qweb': [
        'static/src/xml/financial_reports.xml',
        'static/src/xml/general_ledger.xml',
    ],
}
