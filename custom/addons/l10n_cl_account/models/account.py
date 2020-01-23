from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_cl_invoice_origin_id = fields.Many2one(comodel_name='account.invoice', string='Documento rectificado', readonly=True)
    l10n_cl_e_document = fields.Boolean(related='journal_id.l10n_cl_e_document')

    @api.model
    def default_get(self, fields_list):
        res = super(AccountInvoice, self).default_get(fields_list)
        if self.env.context.get('type', '') in ['out_invoice']:
            journal_obj = self.env['account.journal'].search([('l10n_cl_document_type_id.sii_code', '=', 33)], limit=1)
            res.update({'journal_id': journal_obj and journal_obj.id or False})
        elif self.env.context.get('type', '') in ['out_refund']:
            journal_obj = self.env['account.journal'].search([('l10n_cl_document_type_id.sii_code', '=', 60)], limit=1)
            res.update({'journal_id': journal_obj and journal_obj.id or False})
        return res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        res = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date, description=description, journal_id=journal_id
        )
        journal_id = res.get('journal_id')
        if journal_id and not self.env.context.get("is_pe_debit_note"):
            journal = self.env['account.journal'].browse(journal_id)
            res.update({
                'journal_id': journal.l10n_cl_note_credit_id.id,
            })
        elif journal_id and self.env.context.get("is_pe_debit_note"):
            journal = self.env['account.journal'].browse(journal_id)
            res.update({
                'journal_id': journal.l10n_cl_note_debit_id.id,
                'type': 'out_invoice',
                'refund_invoice_id': False,
            })
        res['l10n_cl_invoice_origin_id'] = invoice.id
        res['date_invoice'] = fields.Date().context_today(self)
        return res


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _get_l10n_cl_activity_domain(self):
        return [('id', 'in', self.env.user.company_id.l10n_cl_activity_ids.ids)]

    l10n_cl_sii_code = fields.Integer(related='l10n_cl_document_type_id.sii_code', string='Código SII', store=True)
    l10n_cl_document_type_id = fields.Many2one(comodel_name='l10n_cl.sii.data', domain=[('table_code', '=', 'sii_table_02')],
                                               string='Tipo de documento')
    l10n_cl_e_document = fields.Boolean(string='Documento electrónico')
    l10n_cl_note_credit_id = fields.Many2one(comodel_name='account.journal', string='Nota de crédito',
                                             domain="[('l10n_cl_document_type_id.sii_code', 'in', [60, 61]),"
                                                    " ('l10n_cl_e_document', '=', l10n_cl_e_document)]")
    l10n_cl_note_debit_id = fields.Many2one(comodel_name='account.journal', string='Nota de débito',
                                            domain="[('l10n_cl_document_type_id.sii_code', 'in', [55, 56]),"
                                                   " ('l10n_cl_e_document', '=', l10n_cl_e_document)]")
    l10n_cl_activity_id = fields.Many2one(comodel_name='l10n_cl.partner.activity', ondelete="restrict", string='Glosa Giro',
                                          domain=_get_l10n_cl_activity_domain)

