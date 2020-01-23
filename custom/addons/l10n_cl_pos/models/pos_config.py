# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = "pos.config"

    pos_auto_invoice = fields.Boolean(string='POS auto invoice', help='POS auto to checked to invoice button', default=1)
    invoice_journal_ids = fields.Many2many(comodel_name='account.journal', relation='pos_config_invoice_journal_rel', column1='config_id',
                                           column2='journal_id', string='Invoice Journal', domain=[('type', '=', 'sale')],
                                           help="Accounting journal used to create invoices.")
    default_partner = fields.Many2one(comodel_name='res.partner', string=_('Default Customer'), domain=[('customer','=',True)])
    set_qty_by_amount = fields.Boolean(string=_('Set quantity by amount'), default=False)
    set_db_notify = fields.Boolean(string=_('Set DB Notify'), default=False)
    fuel_pump_id = fields.Char(string=_('Fuel Pump Id'))
    db_hostname = fields.Char(string=_('DB Hostname'))
    db_port = fields.Char(string=_('DB Port'))
    db_name = fields.Char(string=_('DB Name'))
    db_username = fields.Char(string=_('DB Username'))
    db_password = fields.Char(string=_('DB Password'))
    db_notify = fields.Char(string=_('DB Notify'))
