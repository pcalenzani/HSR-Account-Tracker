from odoo import api, fields, models, Command
import logging

_logger = logging.getLogger(__name__)

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

    character_id = fields.Many2one('sr.character', string='Character', ondelete='cascade')
    light_cone_id = fields.Many2one('sr.light.cone', string='Light Cone', ondelete='cascade')
    # relic_id = fields.Many2one('sr.relic', string='Light Cone', ondelete='cascade')

    def _compute_display_name(self):
        for rec in self:
            val = rec.value
            tag = ''
            if rec.percent:
                val *= 100
                tag = '%'
            # Don't use float_round in str() due to python float multiplication
            rec.display_name = str(round(val, 1)) + tag
    
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
            rec.value = rec.base + rec.addition

    def _set_value(self):
        # If we set value directly, store it as the base amount
        for rec in self:
            rec.base, rec.addition = rec.value, 0.0

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
        commands = [Command.clear()]
        for stats in base:
            stats_done.append(stats['field'])
            for field in ['display']:
                # Remove unused dict values
                stats.pop(field)

            if additional:
                # If two dict lists are provided, split stat value into base + addition
                stats['base'] = stats.pop('value')
                stats['addition'] = next((item['value'] for item in additional if item['field'] == stats['field']), 0.0)
            commands.append(Command.create(stats))
        
        if additional:
            for a_stats in additional:
                if a_stats['field'] in stats_done:
                    # Skip the base stats we've already done
                    continue

                for field in ['display']:
                    # Remove unused dict values
                    a_stats.pop(field)

                # In the additional list, default base to 0 and use addition field
                a_stats['base'] = 0.0
                a_stats['addition'] = a_stats.pop('value')
                commands.append(Command.create(a_stats))
        return commands