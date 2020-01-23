# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Stage(models.Model):
    _inherit = 'note.stage'

    auto_close = fields.Boolean(
            string='Marks as archived',
            help='Marks notes in the stage as archived'
            )

    reverse_auto_close = fields.Boolean(
            string='Undo automatic archive',
            help='Restores a note if it was archived by the stage'
            )


class Note(models.Model):
    _inherit = 'note.note'

    auto_closed_stage_id = fields.Many2one(comodel_name='note.stage')

    related_note_ids = fields.Many2many(
            comodel_name='note.note',
            relation='rel_related_note_note',
            column1='note_id',
            column2='related_note_id'
    )

    @api.multi
    def auto_close(self):
        for record in self:
            record.action_close()
            record.write({'auto_closed_stage_id': record.stage_id.id})

    @api.multi
    def auto_open(self):
        for record in self:
            record.action_open()
            record.write({'auto_closed_stage_id': None})

    @api.multi
    def write(self, values):
        for record in self:
            old_related = self.related_note_ids
            ref = super(Note, record).write(values)
            if not ref:
                return False

            if 'stage_id' in values:
                stage = record.stage_id
                auto_close_stage = record.auto_closed_stage_id
                if stage.auto_close and record.open:
                    record.auto_close()
                elif auto_close_stage and auto_close_stage.reverse_auto_close and not record.open:
                    record.auto_open()

            # Adds this node (record) as related in his related notes
            for note in record.related_note_ids:
                if record not in note.related_note_ids:
                    note.write({
                        'related_note_ids': [(4, record.id)]
                    })

            # Removes other notes that had this as related
            for note in old_related:
                if note not in self.related_note_ids:
                    note.write({'related_note_ids': [(3, record.id)]})

        return True
