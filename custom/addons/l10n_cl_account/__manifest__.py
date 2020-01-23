# -*- coding: utf-8 -*-
{
    "name": "Contabilidad básica de Chile",
    'version': '0.6.0',
    'category': 'Account',
    'sequence': 12,
    'author':  'maicoldlb',
    'website': '',
    'license': 'AGPL-3',
    'summary': """
        Contabilidad básica para la localización de Chile
        """,
    'description': """
        Contabilidad básica para la localización de Chile
        """,
    'depends': [
        'l10n_cl_base',
        'account_invoicing'
        ],
    'data': [
        'data/account.journal.csv',
        'wizard/invoice_refund_view.xml',
        'views/account_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
