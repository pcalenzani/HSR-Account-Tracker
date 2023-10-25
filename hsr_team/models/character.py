from odoo import api, fields, models, tools, Command

# Character Template
class CharacterTemplate(models.Model):
    _name = 'sr.character.template'
    _description = 'Character Template'
    
    avatar = fields.Char("Character Name")
    character_id = fields.Integer('Character ID')
    general_mat_id = fields.Many2one('sr.character.material', string='General Material')
    advanced_mat_id = fields.Many2one('sr.character.material', string='Advanced Material')
    ascension_mat_id = fields.Many2one('sr.character.material', string='Ascension Material')
    eidolon_ids = fields.Many2many('sr.character.eidolon', string='Eidolons')
    warp_ids = fields.One2many('sr.warp', 'character_id', string='Warps')

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

    path = fields.Selection(
        selection=[
            ('Warrior', 'Destruction'),
            ('Priest', 'Abundance'),
            ('Rogue', 'Hunt'),
            ('Mage', 'Erudition'),
            ('Shaman', 'Harmony'),
            ('Warlock', 'Nihility'),
            ('Knight', 'Preservation'),
        ],
        string='Path'
    )

    _sql_constraints = [
        ('character_key', 'UNIQUE (character_id)',  'Duplicate character deteced. Item ID must be unique.')
    ]

    def browse_sr_id(self, sr_ids=None):
        if not sr_ids:
            sr_ids= ()
        elif sr_ids.__class__ is int:
            sr_ids = (sr_ids,)
        else:
            sr_ids= tuple(sr_ids)
            
        self.env.cr.execute(""""SELECT id FROM sr_character_template WHERE character_id in %s""", [sr_ids])
        ids = tuple(self.env.cr.fetchall())
        return self.__class__(self.env, ids, ids)

    def name_get(self):
        return [(rec.id, f"{rec.avatar} (Template)") for rec in self]


class Eidolon(models.Model):
    _name = 'sr.character.eidolon'
    _description = 'Eidolon'

    title = fields.Char('Title')
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
    _description = 'Upgrade Material'

    name = fields.Char("Name")
    type = fields.Selection(
        selection=[
            ('basic', 'General'),
            ('eow', 'Advanced'),
            ('ascension', 'Ascension')
        ]
    )