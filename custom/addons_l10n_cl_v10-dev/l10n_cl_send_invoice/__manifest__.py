# -*- coding: utf-8 -*-
{
    "name": "Send External API invoice",
    'version': '0.6.0',
    'category': 'Localization/Chile',
    'sequence': 12,
    'author':  'maicoldlb',
    'website': 'www.facebook.com/maicoldlb',
    'license': 'AGPL-3',
    'summary': 'Conexión API ODOO 11',
    'description': """
        Envio a API ODOO 11
    """,
    'depends': [
        'account',
    ],
    'data': [
        'views/external_api_view.xml',
        'data/ir.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
