# -*- coding: utf-8 -*-
{
    "name": "API FE openfactura",
    'version': '0.6.0',
    'category': 'Localization/Chile',
    'sequence': 12,
    'author':  'maicoldlb',
    'website': 'https://globalresponse.cl',
    'license': 'AGPL-3',
    'summary': 'Conección a API openfactura para factuación chilena',
    'description': """
        Coneccion a API openfactura para factuacion chilena
    """,
    'depends': [
        'l10n_cl_account',
        'web_download_file'
    ],
    'data': [
        'views/invoice_view.xml',
        'views/res_view.xml',
        'views/openfactura_view.xml',
        'data/openfactura.setting.csv',
        'data/email.xml',
        'security/ir.model.access.csv',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
