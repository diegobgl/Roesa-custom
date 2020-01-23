# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

import json
import base64
import requests


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'download.file']

    openfactura_xml = fields.Binary(string='XML', readonly=True, copy=False)
    openfactura_filename_xml = fields.Char(string='XML', readonly=True, copy=False)
    openfactura_pdf = fields.Binary(string='PDF', readonly=True, copy=False)
    openfactura_filename_pdf = fields.Char(string='PDF', readonly=True, copy=False)
    openfactura_timbre = fields.Binary(string='Timbre', readonly=True, copy=False)
    openfactura_filename_timbre = fields.Char(string='Timbre', readonly=True, copy=False)
    openfactura_token = fields.Char(string='Token', readonly=True, copy=False)
    openfactura_folio = fields.Char(string='Folio')
    
    def _validate_openfactura(self, d, data, msg):
        for index in data.keys():
            if not data.get(index) and d.get(index):
                raise UserError('Complete {} {}'.format(d.get(index), msg))

    def _validate_openfactura_company(self, data):
        d = {
            "RUTEmisor": "Número de documento del socio",
            "RznSoc": "Nombre (incluye razón social)",
            "GiroEmis": "Giros",
            "Acteco": "Actaeco",
            "DirOrigen": "Dirección",
            "CmnaOrigen": "Comuna",
            "CdgSIISucur": 'xx',
            "Telefono": "Teléfono",
        }
        self._validate_openfactura(d, data, 'de la compañia')

    def _validate_openfactura_partner(self, data):
        d = {
            "RUTRecep": "Número de documento",
            "RznSocRecep": "Nombre (incluye razón social)",
            "GiroRecep": "Giro",
            "Contacto": "Telefóno",
            "DirRecep": "Dirección",
            "CmnaRecep": "Comuna",
        }
        self._validate_openfactura(d, data, 'del cliente')

    def _build_openfactura_company(self):
        data = {
            "RUTEmisor": self.company_id.partner_id.l10n_cl_document_number,
            "RznSoc": self.company_id.name,
            "GiroEmis": self.journal_id.l10n_cl_activity_id.name,
            "Acteco": str(self.journal_id.l10n_cl_activity_id.code),
            "DirOrigen": self.company_id.street,
            "CmnaOrigen": self.company_id.partner_id.city_id.name,
            "CdgSIISucur": '81303347',
            "Telefono": self.company_id.phone,
        }
        if self.journal_id.l10n_cl_document_type_id.sii_code == 52:
            data.update({
                'GuiaExport': {'CdgTraslado': '3'}
            })
        self._validate_openfactura_company(data)
        return data

    def _build_openfactura_partner(self):
        if self.journal_id.l10n_cl_document_type_id.sii_code in [39, 41]:
            d = {'RUTRecep': self.partner_id.l10n_cl_document_number or '66666666-6'}
        else:
            d = {
                "RUTRecep": self.partner_id.l10n_cl_document_number,
                "RznSocRecep": self.partner_id.name,
                "GiroRecep": self.partner_id.l10n_cl_activity_ids and self.partner_id.l10n_cl_activity_ids[0].name,
                "Contacto": self.partner_id.phone,
                "DirRecep": self.partner_id.street,
                "CmnaRecep": self.partner_id.city_id.name,
            }
        self._validate_openfactura_partner(d)
        return d

    def _build_openfactura_total(self):
        data = {
            "MntNeto": self.amount_untaxed,
            "TasaIVA": "19" if self.amount_tax else '0',
            "IVA": int(self.amount_tax),
            "MntTotal": int(self.amount_untaxed + int(self.amount_tax))
        }
        if self.journal_id.l10n_cl_document_type_id.sii_code in [34, 43, 52, 55, 60]:
            data.update({
                "MontoPeriodo": self.amount_untaxed,
                "VlrPagar": self.amount_untaxed
            })
        elif self.journal_id.l10n_cl_document_type_id.sii_code in [56, 61]:
            data.update({
                'TotalPeriodo': self.amount_total,
                'VlrPagar': self.amount_total
            })
        if self.journal_id.l10n_cl_document_type_id.sii_code in [34, 41]:
            data.update({'MntExe': self.amount_total})
        return data

    def _validate_openfactura_invoice(self, data):
        d = {
            "TipoDTE": "Tipo de documento",
            "FchEmis": "Fecha de emisión",
            "FmaPago": "2",
            "TpoTranVenta": "Tipo de trans. de venta",
            "TpoTranCompra": "Tipo de trans de compra",
            'IndTraslado': 'Indicador de traslado',
            'TipoDespacho': 'Tipo de despacho',
            'IndServicio': 'Indicador de servicio'
        }
        self._validate_openfactura(d, data, 'de la factura')

    def _build_openfactura_doc(self):
        data = {
            "TipoDTE": self.journal_id.l10n_cl_document_type_id.sii_code,
            "Folio": 0,
            "FchEmis": self.date_invoice,
        }
        if self.journal_id.l10n_cl_document_type_id.sii_code in [33, 34, 43, 52, 56, 61]:
            data.update({"FmaPago": "2"})
            if self.journal_id.l10n_cl_document_type_id.sii_code in [34, 43, 52, 56, 61]:
                data.update({"TpoTranVenta": 1})
                if self.journal_id.l10n_cl_document_type_id.sii_code in [34, 43]:
                    data.update({"TpoTranCompra": 1})
                if self.journal_id.l10n_cl_document_type_id.sii_code in [52]:
                    data.update({
                        'IndTraslado': '3',
                        'TipoDespacho': '2'
                    })
        elif self.journal_id.l10n_cl_document_type_id.sii_code in [39, 41]:
            data.update({'IndServicio': '3'})
        self._validate_openfactura_invoice(data)
        return data

    def _validate_openfactura_reference(self, data):
        d = {
            "TpoDocRef": "Tipo de documento",
            "FolioRef": "Folio",
            "FchRef": "Fecha de documento",
            "CodRef": "Código de referencia"
        }
        self._validate_openfactura(d, data, 'a rectificar')

    def _build_openfactura_reference(self):
        d = list()
        for i, record in enumerate(self.l10n_cl_origin_invoice_id, 1):
            data = {
                "NroLinRef": i,
                "TpoDocRef": record.jounal_id.l10n_cl_document_type_id.sii_code,
                "FolioRef": record.sequence_number_next,
                "FchRef": record.date_invoice,
                "CodRef": "3"
            }
            self._validate_openfactura_reference(data)
            d.append(data)
        return d

    def send_openfactura_invoice(self):
        url = 'https://dev-api.haulmer.com/v2/dte/document'
        token = self.env.user.company_id.openfactura_setting_id.token
        if not token:
            return
        headers = {
            'apikey': token,
        }
        for record in self:
            details = record.invoice_line_ids._build_openfactura_detail()
            company_data = record._build_openfactura_company()
            partner_data = record._build_openfactura_partner()
            totals = record._build_openfactura_total()
            document = record._build_openfactura_doc()
            payload = {
                "response": ["XML", "PDF", "TIMBRE", "LOGO", "FOLIO", "RESOLUCION"],
                "dte": {
                    "Encabezado": {
                        "IdDoc": document,
                        "Emisor": company_data,
                        "Receptor": partner_data,
                        "Totales": totals
                    },
                    "Detalle": details
                }
            }
            if record.journal_id.l10n_cl_document_type_id.sii_code in [52, 56]:
                reference = record._build_openfactura_doc()
                payload['dte'].update({"Referencia": reference})
            r = json.dumps(payload)
            response = requests.request('POST', url, headers=headers, data=r)
            print("DATAs: ", r)
            if response.status_code == 200:
                data = json.loads(response.text)
                record.update({
                    'openfactura_token': data.get('TOKEN'),
                    'openfactura_timbre': data.get('TIMBRE'),
                    'openfactura_xml': data.get('XML'),
                    'openfactura_pdf': data.get('PDF'),
                    'openfactura_filename_pdf': u'{}.pdf'.format(data.get('FOLIO')),
                    'openfactura_filename_xml': u'{}.xml'.format(data.get('FOLIO')),
                    'openfactura_filename_timbre': u'{}.png'.format(data.get('FOLIO')),
                    'openfactura_folio': data.get('FOLIO')
                })
            else:
                raise UserError('Ocurrio un error, consulte con su administrador \n{}'.format(response.text))

    @api.multi
    def action_invoice_sent(self):
        res = super(AccountInvoice, self).action_invoice_sent()
        self.ensure_one()
        if self.openfactura_token:
            file_binary_utf8 = self.openfactura_xml
            template = self.env.ref('l10n_cl_openfactura.email_template_edi_invoice_openfactura', False)
            attach = dict()
            attach['name'] = "%s.xml" % self._get_openfactura_document_name()
            attach['type'] = "binary"
            attach['datas'] = file_binary_utf8
            attach['datas_fname'] = "%s.xml" % self._get_openfactura_document_name()
            attach['res_model'] = "mail.compose.message"
            attachment_id = self.env['ir.attachment'].create(attach)
            attachment_ids = list()
            attachment_ids.append(attachment_id.id)
            attach = dict()
            attach['name'] = "%s.pdf" % self._get_openfactura_document_name()
            attach['type'] = "binary"
            attach['datas'] = self.openfactura_pdf
            attach['datas_fname'] = "%s.pdf" % self._get_openfactura_document_name()
            attach['res_model'] = "mail.compose.message"
            attachment_id = self.env['ir.attachment'].create(attach)
            attachment_ids.append(attachment_id.id)
            vals = dict()
            vals['default_use_template'] = bool(template)
            vals['default_template_id'] = template and template.id or False
            vals['default_attachment_ids'] = [(6, 0, attachment_ids)]
            res['context'].update(vals)
        return res

    @api.multi
    def invoice_print(self):
        if self.openfactura_token:
            return self.action_download_file()
        else:
            return super(AccountInvoice, self).invoice_print()

    def _get_openfactura_document_name(self):
        return self.openfactura_folio or self.number or ''

    def _build_file_content(self):
        return base64.b64decode(self.openfactura_pdf), self._get_openfactura_document_name() + '.pdf'


class AccountInvoiceLines(models.Model):
    _inherit = 'account.invoice.line'

    def _validate_openfactura_detail(self, data):
        d = {
            "NmbItem": "Nombre",
            "QtyItem": "Cantidad",
            "PrcItem": "Precio unitario",
            "MontoItem": "Subtotal",
            "DscItem": "Descripción",
            "TpoDocLiq": "Tipo de documento de liquidación"
        }
        self.invoice_id._validate_openfactura(d, data, 'del detalle')

    def _build_openfactura_detail(self):
        data = list()
        for i, record in enumerate(self, 1):
            d = {
                "NroLinDet": i,
                "NmbItem": record.product_id.name,
                "QtyItem": record.quantity,
                "PrcItem": record.price_unit,
                "MontoItem": record.price_subtotal
            }
            if record.invoice_id.journal_id.l10n_cl_document_type_id.sii_code == 33:
                d.update({"DscItem": record.name})
            if record.invoice_id.journal_id.l10n_cl_document_type_id.sii_code in [34, 41]:
                d.update({
                    "DscItem": record.name,
                    "IndExe": i,
                })
            if record.invoice_id.journal_id.l10n_cl_document_type_id.sii_code == 43:
                d.update({'TpoDocLiq': '33'})
            self._validate_openfactura_detail(d)
            data.append(d)
        return data


