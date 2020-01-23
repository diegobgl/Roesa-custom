# -*- coding: utf-8 -*-
{
    "name": """Base Chile""",
    'version': '0.6.0',
    'category': 'Localization/Chile',
    'sequence': 12,
    'author':  'maicoldlb',
    'website': '',
    'license': 'AGPL-3',
    'summary': """
        Contenido básico para la localización contable de Chile
        """,
    'description': """
        Contenido básico para la localización contable de Chile
        """,
    'depends': [
        'contacts',
        'base_address_city'
        ],
    'data': [
        'data/toponyms.xml',
        'data/country.xml',
        'data/l10n_cl.partner.activity.csv',
        'data/l10n_cl.sii.data.csv',
        'views/l10n_cl_view.xml',
        'views/res_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
