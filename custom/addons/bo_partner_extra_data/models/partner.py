# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    """Member's detail."""

    _inherit = 'res.partner'
    # Falta añadir los campos en la vista
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')], string='Gender')
    occupation = fields.Char('Occupation')
    birthdate = fields.Date('Date of Birth')
