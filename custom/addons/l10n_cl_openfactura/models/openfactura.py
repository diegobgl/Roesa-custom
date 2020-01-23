from odoo import api, fields, models
from odoo.exceptions import UserError

import requests
import json


class OpenfacturaSetting(models.Model):
    _name = 'openfactura.setting'

    name = fields.Char(string='Nombre', required=True)
    token = fields.Char(string='Token', required=True)
    consult_rut = fields.Boolean(string='Consultar rut')


class OpenfacturaInvoice(models.Model):
    _name = 'openfactura.invoice'

    name = fields.Char(string='Nombre', default='/', readonly=True)
    date_invoice = fields.Date(string='Fecha', default=fields.Date().context_today)
    type_date = fields.Selection(selection=[('by_date', 'Por fecha'), ('by_month', 'Por mes')], string='Tipo de fecha', required=True,
                                 default='by_date')
    type_invoice = fields.Selection(selection=[('out_invoice', 'Clientes'), ('in_invoice', 'Proveedores')], string='Tipo de factura',
                                    default='out_invoice', required=True, readonly=True)
    month = fields.Integer(string='Mes')
    year = fields.Integer(string='Año')
    openfactura_line_ids = fields.One2many(comodel_name='openfactura.invoice.line', inverse_name='openfactura_invoice_id', string='Detalle',
                                           readonly=True)
    state = fields.Selection(selection=[('draft', 'Borrador'), ('validate', 'Validado')], string='Estado', default='draft')

    @api.model
    def default_get(self, fields_list):
        res = super(OpenfacturaInvoice, self).default_get(fields_list)
        res.update({
            'year':   fields.Datetime.from_string(fields.Date().context_today(self)).year,
            'month':   fields.Datetime.from_string(fields.Date().context_today(self)).month,
        })
        return res

    @api.multi
    def action_validate(self):
        o_api = self.env['openfactura.api']
        if self.type_date in ['by_date']:
            date = '/'.join(str(self.date_invoice).split('-'))
            datas = o_api._get_registry_sale_by_day(date) if self.type_invoice in ['out_invoice'] else o_api._get_registry_purchase_by_day(date)
        else:
            date = u'{}/{}'.format(self.year, str(self.month).rjust(2, '0'))
            datas = o_api._get_registry_sale_by_month(date) if self.type_invoice in ['out_invoice'] else o_api._get_registry_purchase_by_month(date)

        if not datas:
            raise UserError('Ocurrio un error !')
        datas = json.loads(datas)
        self.openfactura_line_ids.unlink()
        if self.type_invoice in ['out_invoice']:
            self._create_lines(datas)
        else:
            for data in datas:
                self._create_lines(data)
        self.update({'name': date, 'state': 'validate'})

    def _create_lines(self, datas):
        for data in datas.get('registros'):
            sii_data_obj =  self.env['l10n_cl.sii.data'].search(
                [('table_code', 'in', ['sii_table_02']), ('sii_code', '=',  data.get('tipoDocumento'))], limit=1)
            self.env['openfactura.invoice.line'].create({
                'document_type_id': sii_data_obj and sii_data_obj.id or False,
                'amount': data.get('cantDocumentos'),
                'amount_total_ex': data.get('totalMntExe'),
                'amount_total_net': data.get('totalMntNeto'),
                'amount_total_iva': data.get('totalMntIVA'),
                'amount_total': data.get('totalMntTotal'),
                'openfactura_invoice_id': self.id,
                'state': datas.get('estado')
            })


class OpenfacturaInvoiceLine(models.Model):
    _name = 'openfactura.invoice.line'

    document_type_id = fields.Many2one(comodel_name='l10n_cl.sii.data', domain=[('table_code', 'in', ['sii_table_02'])], string='Tipo de documento')
    amount = fields.Integer(string='Cantidad')
    amount_total_ex = fields.Float(string='Monto exento')
    amount_total_net = fields.Float(string='Monto neto')
    amount_total_iva = fields.Float(string='Monto IVA')
    amount_total = fields.Float(string='Monto total')
    openfactura_invoice_id = fields.Many2one(comodel_name='openfactura.invoice', string='Openfactura')
    state = fields.Char(string='Estado')


class OpenfacturaApi(models.AbstractModel):
    _name = 'openfactura.api'

    def _get_response(self, url):
        headers = {'apikey': self.env.user.company_id.openfactura_setting_id.token}
        payload = {}
        try:
            response = requests.request('GET', url, headers=headers, data=payload)
            return response.status_code == 200 and response.text
        except requests.exceptions.ConnectionError:
            raise UserError('Pruebe su conexión a internet!')

    @api.model
    def _get_document(self):
        """
        Corresponde a la petición de la información del Contribuyente ligado a la Apikey.
        Cabe destacar que Openfactura solo genera un solo Api-Key por Contribuyente registrado.
        :return: response text
        """
        url = 'https://dev-api.haulmer.com/v2/dte/organization'
        return self._get_response(url)

    def _get_organization_document(self):
        """
        Proporciona la información de los tipos de documentos que tiene autorizados y
        la cantidad de folios disponibles del contribuyente.
        :return: response text
        """
        url = 'https://dev-api.haulmer.com/v2/dte/organization/document'
        return self._get_response(url)

    def _get_taxprayer_by_rut(self, rut):
        """
        Corresponde a la petición de la información básica de los contribuyentes,
         esta información es la necesaria para la generación de los distintos documentos.
        :param rut:
        :return: response text
        """
        url = 'https://dev-api.haulmer.com/v2/dte/taxpayer/{}'.format(rut)
        return self._get_response(url)

    def _get_registry_sale_by_day(self, date):
        """
        Corresponde a la petición de la información de un registro diario de ventas.
        Retorna la cantidad de documentos emitidos en un día y un resumen de los totales por cada tipo de documento.
        :param date:
        :return: response text
        """
        url = 'https://dev-api.haulmer.com/v2/dte/registry/sales/{}'.format(date)
        return self._get_response(url)

    def _get_registry_sale_by_month(self, date):
        """
        Corresponde a la petición de la información de un registro mensual de emisión de documentos.
        Retorna la cantidad de documentos emitidos en un mes y un resumen de los totales por cada tipo de documento.
        :param date:
        :return: response text
        """
        url = 'https://dev-api.haulmer.com/v2/dte/registry/sales/{}'.format(date)
        return self._get_response(url)

    def _get_registry_purchase_by_day(self, date):
        """
        Corresponde a la petición de la información de un registro diario de Compras.
         Retorna la cantidad de documentos recibidos en un día y un resumen de los totales por cada tipo de documento.
        :param date:
        :return: response text
        """
        url = 'https://dev-api.haulmer.com/v2/dte/registry/purchase/{}?status=pending,registered'.format(date)
        return self._get_response(url)

    def _get_registry_purchase_by_month(self, date):
        """
        Corresponde a la petición de la información de un registro Mensual de Compras.
         Retorna la cantidad de documentos recibidos en un mes y un resumen de los totales por cada tipo de documento.
        :param date:
        :return: response text
        """
        url = 'https://dev-api.haulmer.com/v2/dte/registry/purchase/{}?status=pending,registered'.format(date)
        return self._get_response(url)

    def _get_document_by_token(self, token, value):
        """
        Corresponde a la petición de la información de un documento emitido en Openfactura,
        mediante el token que es generado al emitir el documento , se obtiene la información de ese documento.
        :param token:
        :param value:
        :return: response text
        """
        url = 'https://dev-api.haulmer.com/v2/dte/document/{}/{}'.format(token, value)
        return self._get_response(url)

    def _get_document_by_fields(self, rut, ttype, number, value):
        """
        Corresponde a la petición de la información de un documento emitido o recibido en Openfactura.
        :param rut:
        :param ttype:
        :param number:
        :param value:
        :return: response text
        """
        url = 'https://dev-api.haulmer.com/v2/dte/document/{}/{}/{}/{}'.format(rut, ttype, number, value)
        return self._get_response(url)
