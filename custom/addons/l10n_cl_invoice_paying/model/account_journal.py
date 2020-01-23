# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    type = fields.Selection(selection_add=[('sale_paying', 'Sale Paying'), ('purchase_paying', 'Purchase Paying')])
