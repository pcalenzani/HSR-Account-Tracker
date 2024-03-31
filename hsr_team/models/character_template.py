from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class CharacterTemplate(models.Model):
    _inherit = 'sr.character.template'

    eidolon_ids = fields.One2many('sr.character.eidolon', 'character_template_id', string='Eidolons')
    
    # Relic Slot Distributions
    head = fields.Float('Head Distribution Weight', readonly=True)
    hands = fields.Float('Hands Distribution Weight', readonly=True)
    body = fields.Float('Body Distribution Weight', readonly=True)
    feet = fields.Float('Feet Distribution Weight', readonly=True)
    chain = fields.Float('Chain Distribution Weight', readonly=True)
    orb = fields.Float('Orb Distribution Weight', readonly=True)

    # Stat Weights
    stat_hp = fields.Float('HP Weight', readonly=True)
    stat_atk = fields.Float('Attack Weight', readonly=True)
    stat_def = fields.Float('Defense Weight', readonly=True)
    stat_spd = fields.Float('Speed Weight', readonly=True)
    stat_crit_rate = fields.Float('Crit Rate Weight', readonly=True)
    stat_crit_dmg = fields.Float('Crit Damage Weight', readonly=True)
    stat_sp_rate = fields.Float('Energy Regen Weight', readonly=True)
    stat_effect_res = fields.Float('Effect Resist Weight', readonly=True)
    stat_break_dmg = fields.Float('Break Effect Weight', readonly=True)
    stat_heal_rate = fields.Float('Healing Rate Weight', readonly=True)
    stat_effect_hit = fields.Float('Effect Hit Rate Weight', readonly=True)
    stat_physical_dmg = fields.Float('Physical Damage Weight', readonly=True)
    stat_fire_dmg = fields.Float('Fire Damage Weight', readonly=True)
    stat_ice_dmg = fields.Float('Ice Damage Weight', readonly=True)
    stat_lightning_dmg = fields.Float('Lightning Damage Weight', readonly=True)
    stat_wind_dmg = fields.Float('Wind Damage Weight', readonly=True)
    stat_quantum_dmg = fields.Float('Quantum Damage Weight', readonly=True)
    stat_imaginary_dmg = fields.Float('Imaginary Damage Weight', readonly=True)

    # TODO: Method to check if stat is non-zero (for relic main stat)