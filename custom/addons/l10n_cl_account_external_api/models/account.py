# -*- coding: utf-8 -*-
import ast
from odoo import api, fields, models, SUPERUSER_ID


class L10nclAccountExternalApi(models.Model):
    _name = 'l10n_cl.account.external.api'
    _description = 'Middle invoice table'

    name = fields.Char(string='Nombre', readonly=True)
    date = fields.Date(string='Fecha', default=fields.Date.context_today, readonly=True)
    content = fields.Text(string='Contenido', readonly=True)
    state = fields.Selection(selection=[('draft', 'Borrador'), ('confirmed', 'Confirmado')], default='draft', string='Estado')

    @api.model
    def create(self, vals):
        content = vals.get('content')
        if isinstance(content, str):
            vals.update({'content': ast.literal_eval(content)})
        vals.update({
            'name': self.env['ir.sequence'].next_by_code(self._name),
        })
        return super(L10nclAccountExternalApi, self.sudo(SUPERUSER_ID)).create(vals)

    @api.model
    def get_external_invoice(self):
        for record in self.search([('state', 'in', ['draft'])]):
            for val in ast.literal_eval(record.content):
                self._create_invoice(val)
            record.update({'state': 'confirmed'})

    @api.model
    def _get_partner(self, vals):
        document_obj = self.env['l10n_cl.sii.data'].get_by_sii_code('sii_table_01', vals.get('l10n_cl_document_type_id'))
        country_obj = self.env['res.country'].search([('code', '=', vals.get('country_id'))], limit=1)
        region_obj = self.env['l10n_cl.res.region'].search([('code', '=', vals.get('l10n_cl_res_region_id'))], limit=1)
        state_obj = self.env['res.country.state'].search([('code', '=', vals.get('state_id'))], limit=1)
        city_obj = self.env['res.city'].search([('zipcode', '=', vals.get('city_id'))], limit=1)
        activities_obj = self.env['l10n_cl.partner.activity'].search([('code', 'in', vals.get('l10n_cl_activity_ids', []))])
        company_type = ['company', 'person']
        return self.env['res.partner'].search([('l10n_cl_document_number', '=', vals.get('l10n_cl_document_number'))], limit=1) or \
            self.env['res.partner'].create({
                'name': vals.get('name'),
                'company_type': vals.get('company_type') in company_type and vals.get('company_type') or 'company',
                'l10n_cl_document_type_id': document_obj and document_obj.id or False,
                'l10n_cl_document_number': vals.get('l10n_cl_document_number'),
                'vat': vals.get('l10n_cl_document_number'),
                'street': vals.get('street'),
                'country_id': country_obj and country_obj.id or False,
                'l10n_cl_res_region_id': region_obj and region_obj.id or False,
                'state_id': state_obj and state_obj.id or False,
                'city_id': city_obj and city_obj.id or False,
                'l10n_cl_activity_ids': [(6, 0, activities_obj.ids)],
                'phone': vals.get('phone'),
                'mobile': vals.get('mobile'),
                'email': vals.get('email'),
                'website': vals.get('website')
            })

    @api.model
    def _create_invoice(self, vals):
        partner_obj = self._get_partner(vals.get('partner'))
        journal_obj = self.env['account.journal'].search([('l10n_cl_document_type_id.sii_code', '=', vals.get('l10n_cl_document_type_id'))], limit=1)
        if not journal_obj:
            journal_obj = self.env['account.journal'].search([('l10n_cl_document_type_id.sii_code', '=', 33)], limit=1)
        inv_val = vals.get('invoice')
        if inv_val.get('type') == 'out_paying' and not self.env['ir.module.module'].search(
                [('name', '=', 'l10n_cl_invoice_paying'), ('state', 'in', ['installed'])], limit=1):
            return
        invoice_obj = self.env['account.invoice'].create({
            'partner_id': partner_obj and partner_obj.id or False,
            'journal_id': journal_obj and journal_obj.id or False,
            'account_id': partner_obj.property_account_receivable_id and partner_obj.property_account_receivable_id.id or False,
            'date_invoice': inv_val.get('date_invoice') or fields.Date.context_today(self),
            'date_due': inv_val.get('date_due') or fields.Date.context_today(self),
            'user_id': SUPERUSER_ID,
           # 'type': inv_val.get('type'),
            'name': inv_val.get('name')
        })

        for obj in inv_val.get('lines', []):
            self._create_invoice_line(obj, invoice_obj)

    def _create_invoice_line(self, vals, invoice_id):
        product = self._get_product(vals.get('product'))
        taxes = []
        model_tax = self.env['account.tax']
        for tax in vals.get('invoice_line_tax_ids', []):
            taxes += model_tax.search([('name', '=', tax.get('name')), ('type_tax_use', '=', 'sale')], limit=1).ids or model_tax.create(tax).ids

        line_obj = self.env['account.invoice.line'].create({
            'product_id': product and product.id,
            'name': vals.get('name'),
            'account_id': product.categ_id.property_account_income_categ_id.id,
            'quantity': vals.get('quantity') or 0,
            'price_unit': vals.get('price_unit') or 0,
            'discount': vals.get('discount') or 0,
            'invoice_line_tax_ids': [(6, 0, taxes or product.taxes_id.ids)],
            'invoice_id': invoice_id.id
        })

    def _get_product(self, vals):
        product = self.env['product.product'].search([('name', '=', vals.get('name'))], limit=1)
        if not product:
            taxes = []
            purchase_taxes = []
            model_tax = self.env['account.tax']

            for tax in vals.get('sale_taxes', []):
                taxes += model_tax.search([('name', '=', tax.get('name')), ('type_tax_use', '=', 'sale')], limit=1).ids or \
                         model_tax.create(tax).ids
            for tax in vals.get('purchase_taxes', []):
                purchase_taxes += model_tax.search([('name', '=', tax.get('name')), ('type_tax_use', '=', 'purchase')], limit=1).ids or \
                                  model_tax.create(tax).ids
            product = self.env['product.product'].create({
               'name': vals.get('name'),
               'sale_ok': True,
               'purchase_ok': True,
               'type': vals.get('type'),
               'responsible_id': SUPERUSER_ID,
               'taxes_id': [(6, 0, taxes)],
               'supplier_taxes_id': [(6, 0, purchase_taxes)]
            })
        return product

