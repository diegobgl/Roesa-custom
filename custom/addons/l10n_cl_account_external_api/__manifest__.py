# -*- coding: utf-8 -*-
{
    "name": "External API invoice",
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
        'restful'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/external_api_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
