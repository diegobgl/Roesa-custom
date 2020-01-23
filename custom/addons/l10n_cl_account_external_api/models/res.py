from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def create_external_api_token(self):
        self.env['api.access_token'].find_one_or_create_token(self.id, True)
