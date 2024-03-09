from odoo import api, fields, models

class Eidolon(models.Model):
    _name = 'sr.character.eidolon'
    _description = 'Eidolon'

    title = fields.Char('Title')
    description = fields.Char('Description')
    level = fields.Selection(
        selection=[
            ('rank1', 'Eidolon 1'),
            ('rank2', 'Eidolon 2'),
            ('skill', 'Eidolon 3'),
            ('rank4', 'Eidolon 4'),
            ('ultimate', 'Eidolon 5'),
            ('rank6', 'Eidolon 6'),
        ]
    )
    owned = fields.Boolean('Is Owned')
    character_template_id = fields.Many2one('sr.character.template', string='Character',store=True)
    