# -*- coding: utf-8 -*-
from odoo import models, fields, api
class pos_order(models.Model):
    _inherit = 'pos.order'
    all_free = fields.Boolean(string='All free',default=False)

    @api.model
    def _order_fields(self, ui_order):
        res = super(pos_order, self)._order_fields(ui_order)
        res['all_free'] = ui_order.get('all_free')
        return res

class pos_order_line(models.Model):
    _inherit = 'pos.order.line'
    is_free = fields.Boolean(string='Is free',default=False)

class pos_config(models.Model):
    _inherit = 'pos.config'
    complimentary_using_pin = fields.Boolean(string='Using pin number',default=False)

class res_users(models.Model):
    _inherit = 'res.users'

    @api.model
    def check_pos_security_pin_number(self,pin):
        group_supervisor = self.env.ref('point_of_sale.group_pos_manager')
        supervisors = self.search([('groups_id', 'in', group_supervisor.id)])
        for user in supervisors:
            if user.pos_security_pin == pin:
                return True
        return False