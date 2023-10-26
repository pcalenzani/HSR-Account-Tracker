from odoo import api, fields, models, tools, Command
from odoo.modules import get_module_resource
import requests
import logging
import base64

_logger = logging.getLogger(__name__)

class Item(models.Model):
    _name = 'sr.item'
    _description = 'Item'
    _order = 'item_id DESC'

    item_id = fields.Integer('Item ID')
    name = fields.Char('Name')
    rarity = fields.Selection('Rarity', selection=[
        ('0', 'N/A'),
        ('1', 'N/A'),
        ('2', '2 Star'),
        ('3', '3 Star'),
        ('4', '4 Star'),
        ('5', '5 Star'),
    ])
    level = fields.Integer('Relic Level')

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
    
    def _read_image(self, path):
        if not path:
            return False
        path_info = path.split(',')
        icon_path = get_module_resource(path_info[0], path_info[1])
        image = False
        
        if icon_path:
            with tools.file_open(icon_path, 'rb') as icon_file:
                image = base64.encodebytes(icon_file.read())
        else:
            _logger.error(path_info)
        return image

    def get_image_data(self, img_path):
        if img_path and len(img_path.split(',')) == 2:
            return self._read_image(img_path)

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
    
    rank = fields.Integer('Rank')
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
        characters = super(Character, self).create(vals_list)
        for ch in characters:
            ch.template_id = self.env['sr.character.template'].browse_sr_id(ch.item_id)
            _logger.info(f"New character record: {ch.name}")
        
        return characters
    
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

    rank = fields.Integer('Rank')
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


class Material(models.Model):
    _name = 'sr.item.material'
    _description = 'Upgrade Material'
    _inherit = 'sr.item'

    full_name = fields.Char('Full Name')
    type = fields.Selection(
        selection=[
            ('basic', 'General'),
            ('eow', 'Advanced'),
            ('ascension', 'Ascension')
        ]
    )
    img_path = fields.Char('Image Path')
    image = fields.Binary('Image', store=False, compute='_compute_image')

    @api.depends('img_path')
    def _compute_image(self):
        for rec in self:
            rec.image = rec.get_image_data(rec.img_path)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            path = 'icon/item/%s.png'%(vals['item_id'])
            vals['img_path'] = path
        return super(Material, self).create(vals_list)


# Attributes
# Properties
# Skills