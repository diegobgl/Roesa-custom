# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition, ReportController


class Binary(ReportController):

    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_document(self, model, id, **kwargs):
        res = request.env[model].sudo().browse(int(id))
        file = res._create_file()
        filename = '%s_%s' % (model.replace('.', '_'), id)
        if isinstance(file, int):
            file_content = file
        elif isinstance(file, tuple):
            file_content, filename = file
        if not file_content:
            return request.not_found()
        else:
            xlsxhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(file_content)),
                ('Content-Disposition', content_disposition(filename))
            ]
        return request.make_response(file_content, headers=xlsxhttpheaders)
