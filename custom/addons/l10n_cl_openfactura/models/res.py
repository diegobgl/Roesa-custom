from odoo import api, fields, models

import base64
import json


class ResCompany(models.Model):
    _inherit = 'res.company'

    openfactura_setting_id = fields.Many2one(comodel_name='openfactura.setting', string='Openfactura')
    openfactura_company_info = fields.Binary(string='SII info')
    openfactura_document_info = fields.Binary(string='SII document info')
    openfactura_company_filename = fields.Char(string='SII info')
    openfactura_document_filename = fields.Char(string='SII document info')

    @api.multi
    def _get_openfactura_company_info(self):
        for record in self:
            r = self.env['openfactura.api']._get_document()
            record.update({
                'openfactura_company_info': base64.b64encode(bytes(r, 'utf-8')),
                'openfactura_company_filename': 'company_{}.json'.format(record.partner_id.l10n_cl_document_number)
            })

    @api.multi
    def _get_openfactura_documents_info(self):
        for record in self:
            r = self.env['openfactura.api']._get_organization_document()
            record.update({
                'openfactura_document_info': base64.b64encode(bytes(r, 'utf-8')),
                'openfactura_document_filename': 'documents_{}.json'.format(record.partner_id.l10n_cl_document_number)
            })


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('l10n_cl_document_type_id', 'l10n_cl_document_number')
    def onchange_l10n_cl_document(self):
        res = super(ResPartner, self).onchange_l10n_cl_document()
        if self.env.user.company_id.openfactura_setting_id.consult_rut and self.l10n_cl_document_number:
            self._get_openfactura_activity_info()
        return res

    def _get_openfactura_activity_info(self):
        data = self.get_l10n_cl_partner_data(self.l10n_cl_document_number)
        if data:
            self.update({
                'name': data.get('name') or self.name or '',
                'email': data.get('email') or self.email or '',
                'phone': data.get('phone') or self.phone or '',
                'street': data.get('street') or self.street or '',
                'l10n_cl_activity_ids': [(6, 0, self.l10n_cl_activity_ids.ids + data.get('l10n_cl_activity_ids', []))],
                'city_id': data.get('city_id') or self.city_id or False,
                'state_id': data.get('state_id') or self.state_id or False,
                'l10n_cl_res_region_id': data.get('l10n_cl_res_region_id') or self.l10n_cl_res_region_id.id or False,
                'l10n_cl_document_type_id': data.get('l10n_cl_document_type_id') or self.l10n_cl_document_type_id or False
            })

    @api.model
    def get_l10n_cl_partner_data(self, l10n_cl_document_number):
        res = {}
        r = self.env['openfactura.api']._get_taxprayer_by_rut(l10n_cl_document_number)
        if r:
            data = json.loads(r)
            activity_codes = [str(activity.get('codigoActividadEconomica')) for activity in data.get('actividades')]
            act_obj = self.env['l10n_cl.partner.activity'].search([('code', 'in', activity_codes)])
            city = self.env['res.city'].search([('name', 'in', data.get('comuna'))], limit=1)
            state = city and city.state_id and city.state_id.id or False
            document_obj = self.env['l10n_cl.sii.data'].search([('table_code', '=', 'sii_table_01'), ('code', '=', 'RUT')], limit=1)
            res = {
                'name': data.get('razonSocial') or '',
                'email': data.get('email') or '',
                'phone': data.get('telefono') or '',
                'street': data.get('direccion') or '',
                'l10n_cl_activity_ids': act_obj.ids,
                'city_id': city and city.id or False,
                'state_id': state,
                'l10n_cl_res_region_id': state and state.region_id and state.region_id.id or False,
                'l10n_cl_document_type_id': document_obj and document_obj.id or False
            }
        return res
