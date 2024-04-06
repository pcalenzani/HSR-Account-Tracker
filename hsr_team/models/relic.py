from odoo.tools import json_default
from odoo import api, fields, models, Command

import json
import logging

_logger = logging.getLogger(__name__)

RELIC_SLOTS = [
    ('head', 'Head'),
    ('hands', 'Hands'),
    ('body', 'Body'),
    ('feet', 'Feet'),
    ('orb', 'Planar Sphere'),
    ('chain', 'Link Rope'),
]

STAT_MAX_STEPS = {
    'AttackDelta': 21.168,
    'DefenceDelta': 21.168,
    'HPDelta': 42.337,
    'AttackAddedRatio': 4.32,
    'DefenceAddedRatio': 5.4,
    'HPAddedRatio': 4.32,
    'CriticalChanceBase': 3.24,
    'CriticalDamageBase': 6.48,
    'SpeedDelta': 2.6,
    'StatusResistanceBase': 4.32,
    'StatusProbabilityBase': 4.32,
    'BreakDamageAddedRatioBase': 6.48,
}


class RelicSetBonus(models.Model):
    _name = 'sr.relic.set.bonus'
    _description = 'Set Bonus'
    _order = 'pieces ASC'

    relic_set_id = fields.Many2one('sr.relic.set', string='Relic Set')
    pieces = fields.Selection('Set Pieces', selection=[('2','2-Set Bonus'),('4','4-Set Bonus')])
    bonus = fields.Char('Passive Bonus')


class RelicSet(models.Model):
    _name = 'sr.relic.set'
    _description = 'Relic Set'
    _order = 'id ASC'
    _inherit = 'sr.image.mixin'

    set_id = fields.Integer('Set ID')
    name = fields.Char('Set')

    is_ornament = fields.Boolean('Ornament Set')
    is_relic = fields.Boolean('Relic Set')
    bonus_ids = fields.One2many('sr.relic.set.bonus', 'relic_set_id', string='Set Bonus')
    
    img_id = fields.Many2one('ir.attachment', string='Image', compute='_compute_img_id')

    @api.depends('set_id')
    def _compute_img_id(self):
        # Get image attachment when updating item_id
        # Icon format will be 'icon/relic/116.png'
        img_path = '/hsr_warp/static/icon/relic/'
        for rec in self:
            rec.img_id = rec.get_image_from_path(img_path + str(rec.set_id)).id


class Relic(models.Model):
    _name = 'sr.relic'
    _description = 'Relic'
    _inherit = 'sr.item'

    slot = fields.Selection(string='Relic Slot', selection=RELIC_SLOTS)
    set_id = fields.Many2one('sr.relic.set')
    main_affix_id = fields.Many2one('sr.attribute')
    sub_affix_ids = fields.One2many('sr.attribute', 'relic_id')
    sub_affix_json = fields.Char('Sub Stats JSON', compute='_compute_sub_affix_json')

    character_id = fields.Many2one('sr.character', string='Equipped By', ondelete='cascade')
    score = fields.Float('Relic Score')
    icon = fields.Char('Icon Image Path')
    img_id = fields.Many2one('ir.attachment', string='Image', compute='_compute_img_id')

    def name_get(self):
        return [(rec.id, f"{rec.set_id.name}: {rec.relic_name}") for rec in self]
    
    @api.depends('icon')
    def _compute_img_id(self):
        # Get image attachment when updating item_id
        # Icon format will be 'icon/relic/116_2.png'
        img_path = '/hsr_warp/static/'
        for rec in self:
            rec.img_id = rec.get_image_from_path(img_path + rec.icon).id

    def compute_relic_score(self):
        '''
        Compute relic score by calculating effective stat of all each relic's affixes
        and multiplying by the stat corresponding stat weight of the character equipping it.
        Multiply score by relic slot's weight distribution for the character.

        Sum of relics stats:
            Main stat = 3 * stat weight
            Sub stats = value / maximum stat step
        Potential value:
            55.0 / relic slot weight distribution

        Final score = potential value * sum of relic effective stats
        '''
        for relic in self:
            character = self.character_id.template_id
            relic_score = 0

            # Main stat score
            if relic.slot not in ['head', 'hands']:
                if stat_weight := character.get_stat_weight(relic.main_affix_id.field):
                    # If relic's main stat is a preferred stat (>0), use score of 3 * weight
                    relic_score += 3 * stat_weight

            # Get score of sub stats
            for sub_affix in relic.sub_affix_ids:
                # Effective stat is the stat value divided by highest possible step amount
                effective_stat = sub_affix.value / STAT_MAX_STEPS[sub_affix.attribute]
                stat_weight = character.get_stat_weight(sub_affix.field)
                relic_score += effective_stat * stat_weight
            
            # Score potential scales the possible good stats obtainable per relic
            score_potential = 55.0 / character.get_slot_distribution(relic.slot)
            relic.score = (relic_score * score_potential)

    def _compute_sub_affix_json(self):
        for record in self:
            record.sub_affix_json = json.dumps(record.sub_affix_ids.read(['display_name']), default=json_default)

    @api.model_create_multi
    def create(self, vals_list):
        relics = super().create(vals_list)
        for relic in relics:
            relic.main_affix_id.relic_main_id = relic.id

    def _populate_relics(self, data):
        '''
            id          - Object ID, str
            name        - Name of relic, str
            set_id      - Relic set ID, str
            set_name    - Relic set name, str
            rarity      - Star Rarity, int
            level       - Relic Level, int
            icon        - Relic Image Path, str
            main_affix  - Primary Relic Stat, dict
            sub_affix   - Relic Substats, list(dict)
        '''
        to_remove = ['set_name']
        commands = [Command.clear()]
        Attribute = self.env['sr.attribute']
        if len(data) < 6:
            # Skip relic saving if any empty slots, less headache for slot assignment
            return commands
        for ind, rel in enumerate(data):
            # Remove key if exists
            for k in to_remove: rel.pop(k, None) 
            # Rename id key to db friendly, cast to int for lookup
            rel['item_id'] = int(rel.pop('id'))
            # Get relic slot, relics are received in precise order
            rel['slot'] = RELIC_SLOTS[ind][0]
            # Typecast fields for easy storing
            rel['rarity'] = str(rel.pop('rarity'))
            # Locate set id by reference
            rel['set_id'] = self.env.ref('hsr_team.relic_set_' + rel.pop('set_id')).id
            # Convert affixes into sr.attribute
            rel['main_affix_id'] = Attribute._create_main_affix(rel.pop('main_affix'))
            rel['sub_affix_ids'] = Attribute._populate_attributes(rel.pop('sub_affix'))
            commands.append(Command.create(rel))
        return commands
    
