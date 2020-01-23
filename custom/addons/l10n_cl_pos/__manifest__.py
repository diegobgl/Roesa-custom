# -*- coding: utf-8 -*-
{
    'name': 'Punto de venta',
    'summary': """
        Point Of Sale
        """,
    'version': '11.0.1.0',
    'description': """Point Of Sale""",
    'author': "maicoldlb",
    'website': '',
    'license': "",
    'company': 'maicoldlb',
    'category': 'Point of Sale',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale'
    ],
    "data": [
        "views/pos_templates.xml",
        "views/pos_config_views.xml"
    ],
    'qweb': [
        'static/src/xml/pos_ticket_view.xml',
        'static/src/xml/pos_client_view.xml',
        'static/src/xml/pos_numpad_view.xml'
    ],
    'images': [
        'static/description/icon.jpg'
    ],
    "installable": True,
}
