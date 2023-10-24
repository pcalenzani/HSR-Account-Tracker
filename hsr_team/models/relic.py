from odoo import api, fields, models, tools, Command

class RelicSetBonus(models.Model):
    _name = 'sr.relic.set.bonus'
    _description = 'Relic Bonus'

    # --- Manual Fields ---
    relic_set_id = fields.Many2one('sr.relic.set')

    # --- API Fields ---
    num = fields.Char('Bonus Requirement')
    desc = fields.Char('Description')

    def name_get(self):
        return [(rec.id, f"{rec.num} Set - {rec.relic_set_id.name}") for rec in self]
    
    
class RelicSet(models.Model):
    _name = 'sr.relic.set'
    _description = 'Relic Set'

    # --- Manual Fields ---
    is_ornament = fields.Boolean('Is Ornament Set?')
    is_relic_set = fields.Boolean('Is Relic Set?')

    bonus_ids = fields.One2many('sr.relic.set.bonus', inverse_name='relic_set_id', string='Set Bonuses')

    # --- API Fields ---
    name = fields.Char('Set')
    set_id = fields.Integer('Set ID')


class Relic(models.Model):
    _name = 'sr.relic'
    _description = 'Relic'

    # --- Manual Fields ---
    score = fields.Float('Relic Score')

    # --- API Fields ---
    relic_id = fields.Integer('Relic ID')
    set_id = fields.Many2one('sr.relic.set')
    set_name = fields.Char(related='set_id.name', store=True)
    relic_name = fields.Char('Relic Name')
    rarity = fields.Integer('Rarity')
    level = fields.Integer('Relic Level')
    main_affix = fields.Many2one('sr.relic.affix', string='Main Attribute')
    sub_affix = fields.Many2many('sr.relic.affix', string='Attributes')

    def name_get(self):
        return [(rec.id, f"{rec.set_id.name}: {rec.relic_name}") for rec in self]


class RelicAffix(models.Model):
    _name = 'sr.relic.affix'
    _description = 'Relic Stat'

    # --- Manual Fields ---

    # --- API Fields ---
    type = fields.Char('Attribute Type')
    affix_name = fields.Char('Relic Attribute')
    value = fields.Float('Value')
    display = fields.Char(('Attribute Display'))
    percent = fields.Boolean('Is Percent Amount')
    count = fields.Integer('Affix Count')

    field = fields.Selection(
        selection=[
            ('atk', 'Attack'),
            ('def', 'Defense'),
            ('hp', 'Health'),
            ('crit_rate', 'Crit Rate'),
            ('crit_dmg', 'Crit Damage'),
            ('spd', 'Speed'),
            ('effect_res', 'Effect Res'),
            ('effect_hit', 'Effect Hit Rate'),
            ('break_dmg', 'Break Effect'),
            ('sp_rate', 'Energy Regeneration Rate'),
            ('heal_rate', 'Outgoing Healing Boost'),
            ('quantum_dmg', 'Quantum DMG Boost'),
            ('imaginary_dmg', 'Imaginary DMG Boost'),
            ('lightning_dmg', 'Lightning DMG Boost'),
            ('physical_dmg', 'Physical DMG Boost'),
            ('fire_dmg', 'Fire DMG Boost'),
            ('wind_dmg', 'Wind DMG Boost'),
            ('ice_dmg', 'Ice DMG Boost'),
        ],
        string='Type')

    def name_get(self):
        return [(rec.id, f"{rec.display} {rec.affix_name}") for rec in self]
