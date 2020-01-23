# -*- coding: utf-8 -*-
# Copyright (C) 2018-present  Technaureus Info Solutions Pvt. Ltd.(<http://www.technaureus.com/>).

{
    'name': 'Sales Excel Report',
    'version': '2.0',
    'category': 'Sales',
    'sequence': 1,
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'summary': 'Excel Report Generation',
    'description': """
Generate Sale Report in excel format.
================================

    """,
    'website': 'http://www.technaureus.com',
    'depends': ['sale', 'report_xlsx'],
    'data': [
        'report/sale_report.xml',
        'views/sales_excel_report_views.xml',
        'wizard/excel_wizard.xml',

    ],
    'license': 'Other proprietary',
    'installable': True,
    'application': True,
    'images': ['images/main_screenshot.png']
}
