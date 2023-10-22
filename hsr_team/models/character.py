from odoo import api, fields, models, tools, Command

# Character Template
class CharacterTemplate(models.Model):
    _name = 'sr.character.template'
    _description = 'Character Template'
    
    character_id = fields.Integer('Character ID')
    general_mat_id = fields.Many2one('sr.character.material', string='General Material')
    advanced_mat_id = fields.Many2one('sr.character.material', string='Advanced Material')
    ascension_mad_id = fields.Many2one('sr.character.material', string='Ascension Material')
    eidolon_ids = fields.Many2many('sr.character.eidolon')

    element = fields.Selection(
        selection=[
            ('Wind', 'Wind'),
            ('Ice', 'Ice'),
            ('Physical', 'Physical'),
            ('Fire', 'Fire'),
            ('Quantum', 'Quantum'),
            ('Lightning', 'Lightning'),
            ('Imaginary', 'Imaginary'),
        ],
        string='Element'
    )

class Character(models.Model):
    _name = 'sr.character'
    _description = 'Character'
    _inherit = 'sr.item'
    _order = 'item_id DESC'

    # --- Manual Fields ---
    template_id = fields.Many2one('sr.character.template')
    general_mat_id = fields.Many2one(related='templated_id.general_mad_id')
    advanced_mat_id = fields.Many2one(related='templated_id.advanced_mat_id')
    ascension_mad_id = fields.Many2one(related='templated_id.ascension_mad_id')
    eidolon_ids = fields.Many2many(related='templated_id.eidolon_ids')

    # --- API Fields ---
    promotion = fields.Integer(string='Ascension Level')
    light_cone_id = fields.Many2one('sr.light.cone')
    element = fields.Selection(related='template_id.element')

class Eidolon(models.Model):
    _name = 'sr.character.eidolon'
    _description = 'Eidolon'

    name = fields.Char('Name')
    description = fields.Char('Description')
    level = fields.Selection(
        selection=[
            ('e1', 'Eidolon 1'),
            ('e2', 'Eidolon 2'),
            ('e3', 'Eidolon 3'),
            ('e4', 'Eidolon 4'),
            ('e5', 'Eidolon 5'),
            ('e6', 'Eidolon 6'),
        ]
    )
    owned = fields.Boolean('Is Owned')


class Material(models.Model):
    _name = 'sr.character.material'
    _description = 'Character Material'

    type = fields.Selection(
        selection=[
            ('basic', 'General'),
            ('eow', 'Advanced'),
            ('ascension', 'Ascension')
        ]
    )