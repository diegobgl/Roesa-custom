# -*- coding: utf-8 -*-
# Copyright (C) 2018-present  Technaureus Info Solutions Pvt. Ltd.(<http://www.technaureus.com/>).

import xlsxwriter
from odoo import models


class SalesXlsx(models.AbstractModel):
    _name = 'report.sale_excel_report.sale_report_xls.xslx'
    _inherit = 'report.report_xlsx.abstract'

    def get_lines(self, obj):
        lines = []
        customer = obj.customer_id
        domain = [
            ('date_order', '>=', obj.start_date),
            ('date_order', '<=', obj.end_date),
        ]
        if customer:
            domain.append(('partner_id', '=', customer.id))
        sale_order = self.env['sale.order'].search(domain)
        for value in sale_order:
            state = value.state
            if state == 'draft':
                state = 'Quotation'
            elif state == 'sent':
                state = 'Quotation sent'
            elif state == 'sale':
                state = 'Sales Order'
            elif state == 'done':
                state = 'Locked'
            elif state == 'cancel':
                state = 'Cancelled'
            vals = {
                'name': value.name,
                'customer': value.partner_id.name,
                'amount': value.amount_total,
                'date': value.date_order,
                'state': state
            }
            lines.append(vals)
        return lines

    def generate_xlsx_report(self, workbook, data, wizard_obj):
        for obj in wizard_obj:
            lines = self.get_lines(obj)
            worksheet = workbook.add_worksheet('Report')
            bold = workbook.add_format({'bold': True, 'align': 'center'})
            text = workbook.add_format({'font_size': 12, 'align': 'center'})
            worksheet.set_column(0, 0, 15)
            worksheet.set_column(1, 2, 25)
            worksheet.set_column(3, 3, 15)
            worksheet.set_column(4, 4, 15)
            worksheet.write('A1', 'Order Number', bold)
            worksheet.write('B1', 'Order Date', bold)
            worksheet.write('C1', 'Customer', bold)
            worksheet.write('D1', 'Total', bold)
            worksheet.write('E1', 'Status', bold)
            row = 1
            col = 0
            for res in lines:
                worksheet.write(row, col, res['name'], text)
                worksheet.write(row, col + 1, res['date'], text)
                worksheet.write(row, col + 2, res['customer'], text)
                worksheet.write(row, col + 3, res['amount'], text)
                worksheet.write(row, col + 4, res['state'], text)
                row = row + 1
