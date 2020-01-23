# -*- coding: utf-8 -*-
from odoo import models, fields, api


class L10nclPartnerActivity(models.Model):
    _name = 'l10n_cl.partner.activity'
    _description = 'SII Economical Activities'

    code = fields.Char(string='Activity Code', translate=True)
    parent_id = fields.Many2one('l10n_cl.partner.activity', string='Parent Activity', ondelete='cascade')
    name = fields.Char(string='Nombre Completo', required=True, translate=True)
    iva_affected = fields.Selection(selection=[('yes', 'Si'), ('not', 'No'), ('nd', 'ND')], string='VAT Affected',
                                    translate=True, default='yes')
    tax_category = fields.Selection(selection=[('1', '1'), ('2', '2'), ('nd', 'ND')], string='TAX Category', translate=True,
                                    default='1',)
    internet_available = fields.Boolean(string='Available at Internet', default=True)
    active = fields.Boolean(string='Active', help="Allows you to hide the activity without removing it.", default=True)
    child_ids = fields.One2many(comodel_name='l10n_cl.partner.activity', inverse_name='parent_id', string='Actividades')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|', ('name', '=', name),('code', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search(['|', ('name', operator, name),('code', operator, name)] + args, limit=limit)
        return recs.name_get()


class L10nclSiiData(models.Model):
    _name = 'l10n_cl.sii.data'

    name = fields.Char(string='Name', size=120, required=True)
    code = fields.Char(string='Code', size=16, required=True)
    sii_code = fields.Integer(string='SII Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    table_code = fields.Char(string='Código de tabla')

    """
    @api.model
    def get_selection(self, table_code):
        return self.search([('table_code', '=', table_code)]).mapped(lambda w: (w.sii_code, w.name))
    """

    @api.model
    def get_selection(self, table_code):
        res = list()
        datas = self.search([('table_code', '=', table_code)])
        if datas:
            res = [(data.sii_code, data.name) for data in datas]
        return res

    @api.model
    def get_by_sii_code(self, table_code, sii_code):
        return self.search([('table_code', '=', table_code), ('sii_code', '=', sii_code)], limit=1) or False
