from odoo import api, fields, models, tools, Command
import requests
import logging

_logger = logging.getLogger(__name__)

class Item(models.Model):
    _name = 'sr.item'
    _description = 'Item'
    _order = 'item_id DESC'

    # --- Manual Fields ---

    # --- API Fields ---
    item_id = fields.Integer('Item ID')
    name = fields.Char('Name')


    def get_profile_data(self, user_id=2):
        sr_uid = self.env['res.users'].browse(user_id).sr_uid
        if not sr_uid:
            return
        url = "https://api.mihomo.me/sr_info_parsed/%s?lang=en&version=v2"%(sr_uid)
        response = requests.get(url)

        _logger.info(response.status_code)
        if response.status_code == 200:
            self.env['sr.character'].parse_character_data(response.json()['characters'])
        else:
            _logger.info(url)
            _logger.error(response.reason)
            return
        

class Character(models.Model):
    _name = 'sr.character'
    _description = 'Character'
    _inherit = 'sr.item'
    _order = 'item_id DESC'

    # --- Manual Fields ---
    template_id = fields.Many2one('sr.character.template')
    general_mat_id = fields.Many2one(related='template_id.general_mat_id')
    advanced_mat_id = fields.Many2one(related='template_id.advanced_mat_id')
    ascension_mat_id = fields.Many2one(related='template_id.ascension_mat_id')
    eidolon_ids = fields.One2many(related='template_id.eidolon_ids')
    element = fields.Selection(related='template_id.element', store=True)
    path = fields.Selection(related='template_id.path', store=True)

    count = fields.Integer('Count', store=True, compute='_compute_count')
    is_owned = fields.Boolean('Is Owned', store=True, compute='_compute_count')
    date_obtained = fields.Date('Obtained on')
    free_pulls = fields.Integer('Free Pulls')

    # --- API Fields ---
    promotion = fields.Integer(string='Ascension Level')
    light_cone_id = fields.Many2one('sr.light.cone')
    
    rarity = fields.Integer('Rarity')
    rank = fields.Integer('Rank')
    level = fields.Integer('Level')
    promotion = fields.Integer('Promotion')

    _sql_constraints = [
        ('character_key', 'UNIQUE (item_id)',  'Duplicate character deteced. Item ID must be unique.')
    ]
    
    @api.depends('template_id.warp_ids')
    def _compute_count(self):
        for item in self:
            count = self.env['sr.warp'].search_count([('item_id','=',str(item.item_id))])
            item.count = count
            item.is_owned = count + item.free_pulls
    
    def browse_sr_id(self, sr_ids=None):
        if not sr_ids:
            sr_ids= ()
        elif sr_ids.__class__ is int:
            sr_ids = (sr_ids,)
        else:
            sr_ids= tuple(sr_ids)

        self.env.cr.execute("""SELECT id FROM sr_character WHERE item_id in %s""", [sr_ids])
        ids = tuple(self.env.cr.fetchall())
        return self.__class__(self.env, ids, ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        characters = super().create(vals_list)
        for ch in characters:
            ch.template_id = self.env['sr.character.template'].browse_sr_id(ch.item_id)
            _logger.info(f"New character record: {ch.name}")
    
    def parse_character_data(self, data):
        for ch in data:
            ch_rec = self.browse_sr_id(ch['id'])
            if not ch_rec:
                # Create new item
                self._create_character_json(ch)
            else:
                # Update item
                pass
            
    def _create_character_json(self, ch_data):
        to_remove = [
            'icon',
            'preview',
            'portrait',
            'rank_icons',
            'element',
            'path',
            'skills',
            'skill_trees',
            'light_cone',
            'relics',
            'relic_sets',
            'attributes',
            'additions',
            'properties',
        ]
        for k in to_remove:
            if k in ch_data:
                del ch_data[k]
        
        ch_data['item_id'] = ch_data.pop('id')
        self.create(ch_data)
    

class LightCone(models.Model):
    _name = 'sr.light.cone'
    _description = 'Light Cone'
    _inherit = 'sr.item'
    _order = 'item_id DESC'

    rarity = fields.Integer('Rarity')
    rank = fields.Integer('Rank')
    level = fields.Integer('Level')
    promotion = fields.Integer('Superimposition')

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


class Warp(models.Model):
    _inherit = 'sr.warp'

    character_id = fields.Many2one('sr.character', store=True, compute='_compute_character_id')

    def _compute_character_id(self):
        for warp in self:
            warp.character_id = self.env['sr.character.template'].search([('character_id','=',warp.item_id)])

# Attributes
# Properties
# Skills