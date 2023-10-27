from odoo import api, fields, models, tools, Command

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
    character_template_id = fields.Many2one('sr.character.template', string='Character',store=True)
    character_item_id = fields.Integer(related='character_template_id.character_id')