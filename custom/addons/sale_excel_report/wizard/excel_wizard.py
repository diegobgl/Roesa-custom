# -*- coding: utf-8 -*-
# Copyright (C) 2018-present  Technaureus Info Solutions Pvt. Ltd.(<http://www.technaureus.com/>).

import datetime
from odoo import api, fields, models


class SaleExcelWizard(models.TransientModel):
    _name = 'sale.excel.wizard'

    customer_id = fields.Many2one('res.partner', string="Customer")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date", default=fields.Date.today)

    @api.multi
    def print_xls_report(self, context=None):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.excel.wizard'
        datas['form'] = self.read()[0]
        return self.env.ref('sale_excel_report.sale_report_xls').report_action(self, data=datas)
