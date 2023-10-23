from odoo import api, fields, models, tools, Command

class Item(models.Model):
    _name = 'sr.item'
    _description = 'Item'
    _order = 'item_id DESC'

    # --- Manual Fields ---
    count = fields.Integer('Count', compute='_compute_count')
    is_owned = fields.Boolean('Is Owned')
    date_obtained = fields.Date('Obtained on')

    # --- API Fields ---
    item_id = fields.Integer('Item ID')
    name = fields.Char('Name')
    rarity = fields.Integer('Rarity')
    rank = fields.Integer('Rank')
    level = fields.Integer('Level')
    promotion = fields.Integer('Promotion')

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

    def _compute_count(self):
        self.count = self.env['sr.warp'].search_count([('item_id','=',str(self.item_id))])


class LightCone(models.Model):
    _name = 'sr.light.cone'
    _description = 'Light Cone'
    _inherit = 'sr.item'
    _order = 'item_id DESC'

    promotion = fields.Integer(string='Superimposition')
    


# Attributes
# Properties
# Skills