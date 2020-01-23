# -*- coding: utf-8 -*-

from odoo import models, api


class DownloadFile(models.AbstractModel):
    _name = 'download.file'

    @api.multi
    def action_download_file(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=%s&id=%s' % (self._name, self.id),
            'target': 'self',
        }

    @api.multi
    def _create_file(self):
        file_base64, filename = self._build_file_content()
        return file_base64, filename

    def _build_file_content(self):
        pass



