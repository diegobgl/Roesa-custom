# -*- coding: utf-8 -*-
{
    'name': 'Notes Extended',
    'version': '11.0.1.0.0',
    'description': """Adds extra functionality to Odoo Notes""",
    'summary': 'Auto archive and related notes',
    'author': 'Hugo Rodrigues',
    'website': 'https://hugorodrigues.net',
    'license': 'Other OSI approved licence',
    'category': 'Tools',
    'depends': [
        'note',
    ],
    'data': [
        'views/note_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_instal': False
}
