# -*- coding: utf-8 -*-
from odoo import api, fields, models
import requests
import json


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_cl_is_sent = fields.Boolean(string='Factura enviada', copy=False)

    @api.model
    def l10n_cl_massive_send_invoice(self):
        self.search([
            ('l10n_cl_is_sent', '=', True),
            ('state', 'in', ['open', 'paid']),
            ('type', 'in', ['out_invoice', 'out_refund', 'out_paying'])
        ], limit=50).l10n_cl_send_data()

    @api.multi
    def l10n_cl_send_data(self):
        content = list()

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'access-token': self.env['ir.config_parameter'].sudo().get_param('external_api_token')
        }

        base_url = self.env['ir.config_parameter'].sudo().get_param('external_api_url')
        for record in self.filtered(lambda w: not w.l10n_cl_is_sent):
            record.l10n_cl_is_sent = True
            content.append({
                "partner": {
                    "name": record.partner_id.name,
                    "l10n_cl_document_type_id": 81,
                    "l10n_cl_document_number": (record.partner_id.vat or '').replace('.', ''),
                    "street": record.partner_id.street or '',
                    "country_id": record.partner_id.country_id.code,
                    "state_id": record.partner_id.state_id.code or '',
                    "phone": record.partner_id.phone or '',
                    "email": record.partner_id.email or '',
                    #"city_id": record.partner_id.city_id.code or '',
                    "company_type": record.partner_id.company_type or ''
                },
                "invoice": {
                    "number": record.number,
                    "name": record.number,
                    "date_invoice": record.date_invoice,
                    "date_due": record.date_due,
                    "type": record.type,
                    "type": record.type,
                    "lines": record.invoice_line_ids.mapped(lambda item: {
                        "product": {
                            "name": item.product_id.name,
                            "type": item.product_id.type,
                            "sale_taxes": item.product_id.taxes_id.mapped(
                                lambda w: {
                                    'name': w.name,
                                    'amount': w.amount,
                                    'description': w.description,
                                    'type_tax_use': w.type_tax_use
                                }),
                            "purchase_taxes": item.product_id.supplier_taxes_id.mapped(
                                lambda w: {
                                    'name': w.name,
                                    'amount': w.amount,
                                    'description': w.description,
                                    'type_tax_use': w.type_tax_use
                                })
                        },
                        "name": item.name,
                        "quantity": item.quantity,
                        "price_unit": item.price_unit,
                        "discount": item.discount,
                        "invoice_line_tax_ids": item.invoice_line_tax_ids.mapped(lambda w: {
                                    'name': w.name,
                                    'amount': w.amount,
                                    'description': w.description,
                                    'type_tax_use': w.type_tax_use
                                }),
                    })
                }
            })
        if content:
            url = '%s/api/l10n_cl.account.external.api/' % base_url
            r = requests.post(url, headers=headers, data={'content': json.dumps(str(content))})
            print "status_code: ", r.status_code
