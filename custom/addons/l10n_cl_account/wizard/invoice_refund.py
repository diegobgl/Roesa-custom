# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.model
    def default_get(self, fields_list):
        res = super(AccountInvoiceRefund, self).default_get(fields_list)
        invoice_obj = self.env['account.invoice'].browse(self.env.context.get('active_id'))
        journal_obj = invoice_obj.journal_id
        if journal_obj.l10n_cl_document_type_id and not (journal_obj.l10n_cl_note_debit_id or journal_obj.l10n_cl_note_credit_id):
            raise UserError('Configure secuencia para NC y ND en secuencia: {}'.format(journal_obj.l10n_cl_document_type_id.name))
        return res

    @api.multi
    def invoice_refund(self):
        res = super(AccountInvoiceRefund, self).invoice_refund()
        if self.env.context.get("is_pe_debit_note", False):
            invoice_domain = res['domain']
            if invoice_domain:
                del invoice_domain[0]
                res['domain'] = invoice_domain
        return res
