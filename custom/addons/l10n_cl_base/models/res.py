from odoo import api, fields, models, _
from odoo.exceptions import UserError

import re


class ResCountry(models.Model):
    _inherit = 'res.country'

    l10n_cl_rut_natural = fields.Char('RUT persona natural', size=11)
    l10n_cl_rut_legal = fields.Char('RUT persona juridica', size=11)
    l10n_cl_rut_other = fields.Char('RUT otro', size=11)
    l10n_cl_region_ids = fields.One2many(comodel_name='l10n_cl.res.region', inverse_name='country_id', string='Regiones')


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    l10n_cl_region_id = fields.Many2one(comodel_name='l10n_cl.res.region', string='Region', index=True)
    l10n_cl_city_ids = fields.One2many(comodel_name='res.city', inverse_name='state_id', string='Comunas')


class ResCity(models.Model):
    _inherit = 'res.city'

    l10n_cl_code = fields.Char(string='City Code', help='The city code.\n', required=True)


class L10nclResRegion(models.Model):
    _name = 'l10n_cl.res.region'

    name = fields.Char(string='Region Name', help='The state code.\n', required=True)
    code = fields.Char(string='Region Code', help='The region code.\n', required=True)
    country_id = fields.Many2one(comodel_name='res.country', string='País')
    state_ids = fields.One2many(comodel_name='res.country.state', inverse_name='l10n_cl_region_id', string='Child Regions')


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_cl_activity_ids = fields.Many2many(comodel_name='l10n_cl.partner.activity', id1='company_id', id2='activities_id',
                                            domain=[('parent_id', '!=', False), ('child_ids', '=', False)], string='Actividades')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_cl_document_type_id = fields.Many2one(comodel_name='l10n_cl.sii.data', domain=[('table_code', 'in', ['sii_table_01'])],
                                               placeholder='Tipo de documento')
    l10n_cl_document_number = fields.Char(string='Document number', size=64)
    l10n_cl_activity_ids = fields.Many2many(comodel_name='l10n_cl.partner.activity', ondelete="restrict", string='Actividades',
                                            domain=[('parent_id', '!=', False), ('child_ids', '!=', False)])
    l10n_cl_res_region_id = fields.Many2one(comodel_name='l10n_cl.res.region', domain="[('country_id', '=', country_id)]")

    @api.model
    def default_get(self, fields_list):
        res = super(ResPartner, self).default_get(fields_list)
        country = self.env['res.country'].search([('code', 'in', ['CL'])], limit=1)
        res.update({
            'country_id': country and country.id or False
        })
        return res

    @api.onchange('l10n_cl_document_type_id', 'l10n_cl_document_number')
    def onchange_l10n_cl_document(self):
        if self.l10n_cl_document_number:
            l10n_cl_document_number = (re.sub('[^1234567890Kk]', '', str(self.l10n_cl_document_number))).zfill(9).upper()
            if not self.check_vat_cl(l10n_cl_document_number):
                return {
                    'warning': {
                        'title': _('Rut Erróneo'),
                        'message': _('Rut Erróneo'),
                    }
                }
            vat = 'CL%s' % l10n_cl_document_number
            exist = self.env['res.partner'].search([
                ('vat', '=', vat), ('vat', '!=',  'CL555555555'), ('commercial_partner_id', '!=', self.commercial_partner_id.id)], limit=1)
            if exist:
                self.vat = ''
                self.l10n_cl_document_number = ''
                return {
                    'warning': {
                        'title': 'Informacion para el Usuario',
                        'message': _("El usuario %s está utilizando este documento" ) % exist.name,
                    }
                }
            self.vat = vat
        else:
            self.vat = ''

    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id:
            self.country_id = self.city_id.state_id.country_id.id
            self.state_id = self.city_id.state_id.id
            self.city = self.city_id.name

    @api.onchange('country_id')
    def _onchange_country_id(self):
        pass

    @api.constrains('vat', 'commercial_partner_id')
    def _rut_unique(self):
        for r in self:
            if not r.vat or r.parent_id:
                continue
            partner = self.env['res.partner'].search(
                [('vat', '=', r.vat), ('id', '!=', r.id), ('commercial_partner_id', '!=', r.commercial_partner_id.id)])
            if r.vat != "CL555555555" and partner:
                raise UserError(_('El rut: %s debe ser único') % r.vat)

    def check_vat_cl(self, vat):
        if len(vat) != 9:
            return False
        else:
            body, vdig = vat[:-1], vat[-1].upper()
        try:
            vali = list(range(2, 8)) + [2, 3]
            operar = '0123456789K0'[11 - (sum([int(digit)*factor for digit, factor in zip(body[::-1], vali)]) % 11)]
            if operar == vdig:
                return True
            else:
                return False
        except IndexError:
            return False

    @api.model
    def _get_l10n_cl_partner_data(self, l10n_cl_document_number):
        return {}
