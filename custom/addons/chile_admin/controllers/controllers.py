# -*- coding: utf-8 -*-
from odoo import http

# class ChileAdmin(http.Controller):
#     @http.route('/chile_admin/chile_admin/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/chile_admin/chile_admin/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('chile_admin.listing', {
#             'root': '/chile_admin/chile_admin',
#             'objects': http.request.env['chile_admin.chile_admin'].search([]),
#         })

#     @http.route('/chile_admin/chile_admin/objects/<model("chile_admin.chile_admin"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('chile_admin.object', {
#             'object': obj
#         })