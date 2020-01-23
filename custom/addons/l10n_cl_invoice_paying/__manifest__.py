# -*- coding: utf-8 -*-
{
    'name': 'Documentos Tributarios - Chile',
    'version': '1.0',
    'category': 'Localization/Chile',
    "description": """
        Liquidación Factura
    """,
    'author': 'maicoldlb',
    'website': '',
    'depends': [
         'account_voucher'
    ],
    'data': [
        'view/account_invoice.xml',
        'view/account_reports.xml',
    ],
    'installable': True,
    'active': False,
}