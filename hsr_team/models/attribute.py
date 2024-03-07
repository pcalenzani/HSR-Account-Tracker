from odoo import api, fields, models, tools, Command
import logging

_logger = logging.getLogger(__name__)

class Attribute(models.Model):
    _name = 'sr.attribute'
    _description = 'Character Stat'

    name = fields.Char('Name')
    field = fields.Char('Stat Reference')
    value = fields.Float('Value', compute='_compute_value')
    percent = fields.Boolean('Is Percent')

    # Character attribute values will be split on receipt
    base = fields.Float('Base Value', default=0.0)
    addition = fields.Float('Added Value', default=0.0)

    # -- Relic Affix Fields ---
    attribute = fields.Char('Type') # This field is named 'type' in API
    count = fields.Integer('Count') # Times leveled, base = 1
    step = fields.Integer('Step') # Affix base amount step

    character_id = fields.Many2one('sr.character', string='Character', ondelete='cascade')
    # relic_id = ...

    @api.depends('base', 'addition')
    def _compute_value(self):
        for record in self:
            record.value = record.base + record.addition
