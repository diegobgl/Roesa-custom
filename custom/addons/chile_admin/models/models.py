# -*- coding: utf-8 -*-

from odoo import models, fields, api

class chile_admin(models.Model):
     _name = 'chile_admin.chile_admin'

     nombre_alumno = fields.Char()
     apwllido_alumno = fields.Integer()
     edad_alumno = fields.Float(compute="_value_pc", store=True)
     description = fields.Text()

     @api.depends('value')
     def _value_pc(self):
         self.value2 = float(self.value) / 100