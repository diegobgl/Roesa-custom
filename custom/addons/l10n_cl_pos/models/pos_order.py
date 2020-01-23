# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosOrder(models.Model):
    _inherit = "pos.order"

    invoice_journal_id = fields.Many2one(comodel_name='account.journal', string='Journal account', readonly=1)

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        if 'invoice_journal_id' in ui_order:
            res['invoice_journal_id'] = ui_order['invoice_journal_id']
        return res

    def _prepare_invoice(self):
        res = super(PosOrder, self)._prepare_invoice()
        if self.invoice_journal_id:
            res['journal_id'] = self.invoice_journal_id.id
        return res

