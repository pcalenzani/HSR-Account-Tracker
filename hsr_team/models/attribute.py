from odoo import api, fields, models, tools, Command
import logging

_logger = logging.getLogger(__name__)

class Attribute(models.Model):
    _name = 'sr.attribute'
    _description = 'Character Stat'

    name = fields.Char('Name')
    field = fields.Char('Stat Reference')
    value = fields.Float('Value', store=True, compute='_compute_value', inverse='_set_value')
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

    def _set_value(self):
        # If we set value directly, store it as the base amount
        for record in self:
            record.base, record.addition = record.value, 0.0

    def _populate_attributes(self, base, additional=None):
        '''
        Receive list of values to create attributes. Used for character and relics.
        - Characters: Receive base stats and additional stats, need to sum together
        - Relics: Receive a main stat value and substat list
        :param statlist: list of attribute dictionaries
                type        - attribute, str
                field       - field, str
                name        - name, str
                icon        - Path to icon image, str
                value       - base or addition, float
                display     - Display string for value, str
                percent     - percent
        :param additional: list of additional attributes for characters only
        :returns: list of values ready for Command create call
        '''
        stats_done = [] # when using both base and additional, need to track which stats we've appended
        commands = []
        for stats in base:
            stats_done.append(stats['field'])
            for field in ['icon', 'display']:
                # Remove unused dict values
                stats.pop(field)

            if additional:
                # If two dict lists are provided, split stat value into base + addition
                stats['base'] = stats.pop('value')
                stats['addition'] = next((item for item in additional if item['field'] == stats['field']), 0.0)['value']
            commands.append(Command.create(stats))
        
        if additional:
            for a_stats in additional:
                if a_stats['field'] in stats_done:
                    # Skip the base stats we've already done
                    continue

                for field in ['icon', 'display']:
                    # Remove unused dict values
                    a_stats.pop(field)

                # In the additional list, default base to 0 and use addition field
                a_stats['base'] = 0.0
                a_stats['addition'] = a_stats.pop('value')
                commands.append(Command.create(a_stats))
        return commands