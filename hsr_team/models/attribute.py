from odoo import api, fields, models, Command
import logging

_logger = logging.getLogger(__name__)

'''
'atk', 'Attack'
'def', 'Defense'
'hp', 'Health'
'crit_rate', 'Crit Rate'
'crit_dmg', 'Crit Damage'
'spd', 'Speed'
'effect_res', 'Effect Res'
'effect_hit', 'Effect Hit Rate'
'break_dmg', 'Break Effect'
'sp_rate', 'Energy Regeneration Rate'
'heal_rate', 'Outgoing Healing Boost'
'quantum_dmg', 'Quantum DMG Boost'
'imaginary_dmg', 'Imaginary DMG Boost'
'lightning_dmg', 'Lightning DMG Boost'
'physical_dmg', 'Physical DMG Boost'
'fire_dmg', 'Fire DMG Boost'
'wind_dmg', 'Wind DMG Boost'
'ice_dmg', 'Ice DMG Boost'
'''

class Attribute(models.Model):
    _name = 'sr.attribute'
    _description = 'Character Stat'
    _inherit = 'sr.image.mixin'

    name = fields.Char('Name')
    field = fields.Char('Stat Reference')
    value = fields.Float('Value', store=True, compute='_compute_value', inverse='_set_value')
    percent = fields.Boolean('Is Percent')

    icon = fields.Char('Icon Image Path')
    img_id = fields.Many2one('ir.attachment', string='Image', compute='_compute_img_id')

    # Character attribute values will be split on receipt
    base = fields.Float('Base Value', default=0.0)
    addition = fields.Float('Added Value', default=0.0)

    # -- Relic Affix Fields ---
    attribute = fields.Char('Type') # This field is named 'type' in API
    count = fields.Integer('Count') # Times leveled, base = 1
    step = fields.Integer('Step') # Affix base amount step

    # Attributes only exist as part of character or relics, delete when the link is gone
    character_id = fields.Many2one('sr.character', string='Character', ondelete='cascade')
    light_cone_id = fields.Many2one('sr.light.cone', string='Light Cone', ondelete='cascade')
    relic_id = fields.Many2one('sr.relic', string='Relic', ondelete='cascade')
    relic_main_id = fields.Many2one('sr.relic', string='Relic (Main Affix)', ondelete='cascade')

    def _compute_display_name(self):
        for rec in self:
            tag = ''
            if rec.percent:
                tag = '%'
            # Don't use float_round in str() due to python float multiplication
            rec.display_name = str(round(rec.value, 1)) + tag
    
    @api.depends('icon')
    def _compute_img_id(self):
        # Get image attachment when updating item_id
        # Icon format will be 'icon/property/IconMaxHP.png'
        img_path = '/hsr_warp/static/'
        for rec in self:
            rec.img_id = rec.get_image_from_path(img_path + rec.icon).id

    @api.depends('base', 'addition')
    def _compute_value(self):
        for rec in self:
            value = rec.base + rec.addition
            rec.value = value if not rec.percent else value * 100

    def _set_value(self):
        # If we set value directly, store it as the base amount
        for rec in self:
            value = rec.value / 100 if rec.percent else rec.value
            rec.base, rec.addition = value, 0.0

    def _populate_attributes(self, base, additional=None):
        '''
        Receive list of values to create attributes. Used for character and relics.
        - Characters: Receive base stats and additional stats, need to sum together
        - Relics: Receive a main stat value and substat list
        :param statlist: list of attribute dictionaries
                type        - Specific Stat Type for Relic (HPAddedRatio), str
                field       - General Stat Category (hp), str
                name        - Attribute Name, str
                icon        - Path to icon image, str
                value       - base or addition, float
                display     - Display string for value, str
                percent     - Percent Stat flag, bool
                count       - Times leveled for Relic, int
                step        - Base Amount for Relic, int
        :param additional: list of additional attributes for characters only
        :returns: list of values ready for Command create call
        '''
        stats_done = [] # when using both base and additional, need to track which stats we've appended
        commands = [Command.clear()]
        for stats in base:
            stats_done.append(stats['field'])
            # Remove unused dict values
            for field in ['display']: stats.pop(field)
            stats['attribute'] = stats.pop('type', None)
                
            if additional:
                # If two dict lists are provided, split stat value into base + addition
                stats['base'] = stats.pop('value')
                stats['addition'] = next((item['value'] for item in additional if item['field'] == stats['field']), 0.0)
            else:
                if stats['percent']:
                    stats['value'] = stats['value'] * 100
            commands.append(Command.create(stats))
        
        if additional:
            for a_stats in additional:
                if a_stats['field'] in stats_done:
                    # Skip the base stats we've already done
                    continue
                # Remove unused dict values
                for field in ['display']: a_stats.pop(field)
                stats['attribute'] = stats.pop('type', None)
                
                # In the additional list, default base to 0 and use addition field
                a_stats['base'] = 0.0
                a_stats['addition'] = a_stats.pop('value')
                commands.append(Command.create(a_stats))
        return commands
        
    def _create_main_affix(self, data):
        '''
        Creates sr.attribute record for relic main affix, expects single data set
        :param data: dictionary of main affix values
        :returns: id of created sr.attribute record
        '''
        return self.create({
            'name': data['name'],
            'field': data['field'],
            'attribute': data['type'],
            'value': data['value'],
            'percent': data['percent'],
            'icon': data['icon'],
        }).id