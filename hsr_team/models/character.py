from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class CharacterTemplate(models.Model):
    _inherit = 'sr.character.template'

    eidolon_ids = fields.One2many('sr.character.eidolon', 'character_template_id', string='Eidolons')

    # -- Materials --
    general_mat_id = fields.Many2one('sr.item.material', string='General Material')
    general_mat_img_id = fields.Many2one(related='general_mat_id.img_id', string='General Material Image')
    advanced_mat_id = fields.Many2one('sr.item.material', string='Advanced Material')
    advanced_mat_img_id = fields.Many2one(related='advanced_mat_id.img_id', string='Advanced Material Image')
    ascension_mat_id = fields.Many2one('sr.item.material', string='Ascension Material')
    ascension_mat_img_id = fields.Many2one(related='ascension_mat_id.img_id', string='Ascension Material Image')

class Character(models.Model):
    _name = 'sr.character'
    _description = 'Character'
    _inherit = 'sr.item'
    _order = 'item_id DESC'

    # --- Template Fields ---
    template_id = fields.Many2one('sr.character.template')
    warp_ids = fields.One2many(related='template_id.warp_ids')
    light_cone_id = fields.Many2one('sr.light.cone')
    light_cone_img_id = fields.Many2one(related='light_cone_id.preview_img_id')

    element_id = fields.Many2one(related='template_id.element_id')
    element_img_id = fields.Many2one(related='template_id.element_id.img_id', string='Element Image')
    path_id = fields.Many2one(related='template_id.path_id')
    path_img_id = fields.Many2one(related='template_id.path_id.img_id', string='Path Image')
    eidolon_ids = fields.One2many(related='template_id.eidolon_ids')

    general_mat_id = fields.Many2one(related='template_id.general_mat_id')
    general_mat_img_id = fields.Many2one(related='template_id.general_mat_id.img_id', string='General Mat Image')
    advanced_mat_id = fields.Many2one(related='template_id.advanced_mat_id')
    advanced_mat_img_id = fields.Many2one(related='template_id.advanced_mat_id.img_id', string='Advanced Mat Image')
    ascension_mat_id = fields.Many2one(related='template_id.ascension_mat_id')
    ascension_mat_img_id = fields.Many2one(related='template_id.ascension_mat_id.img_id', string='Ascension Mat Image')

    portrait_path = fields.Char('Portrait Image Path')
    preview_path = fields.Char('Preview Image Path')
    icon_path = fields.Char('Icon Image Path')
    portrait_img_id = fields.Many2one('ir.attachment', string='Portrait Image', compute='_compute_images')
    preview_img_id = fields.Many2one('ir.attachment', string='Preview Image', compute='_compute_images')
    icon_img_id = fields.Many2one('ir.attachment', string='Icon Image', compute='_compute_images')

    # --- Manual Fields ---
    count = fields.Integer('Count', store=True, compute='_compute_count')
    is_owned = fields.Boolean('Is Owned', store=True, compute='_compute_count')
    date_obtained = fields.Date('Obtained on')
    free_pulls = fields.Integer('Free Pulls')

    # --- API Fields ---
    promotion = fields.Integer(string='Ascension Level')
    rank = fields.Integer('Eidolon Level')
    promotion = fields.Integer('Promotion')

    # --- Stat Fields ---
    attribute_ids = fields.One2many('sr.attribute', 'character_id', string='Character Stats', inverse='_set_attributes')
    att_hp = fields.Many2one('sr.attribute', string='HP Stat')
    att_atk = fields.Many2one('sr.attribute', string='ATK Stat')
    att_def = fields.Many2one('sr.attribute', string='DEF Stat')
    att_spd = fields.Many2one('sr.attribute', string='SPD Stat')
    att_crit_rate = fields.Many2one('sr.attribute', string='CRIT_RATE Stat')
    att_crit_dmg = fields.Many2one('sr.attribute', string='CRIT_DMG Stat')
    
    _sql_constraints = [
        ('character_key', 'UNIQUE (item_id)',  'Duplicate character deteced. Item ID must be unique.')
    ]
    
    @api.depends('template_id.warp_ids')
    def _compute_count(self):
        for rec in self:
            count = self.env['sr.warp'].search_count([('item_id','=',str(rec.item_id))])
            rec.count = count
            rec.is_owned = count + rec.free_pulls

    @api.depends('icon_path', 'preview_path', 'portrait_path')
    def _compute_images(self):
        for rec in self:
            rec.portrait_img_id = rec.get_image_from_path(rec.portrait_path, field='portrait_img_id').id
            rec.preview_img_id = rec.get_image_from_path(rec.preview_path, field='preview_img_id').id
            rec.icon_img_id = rec.get_image_from_path(rec.icon_path, field='icon_img_id').id

    def _set_attributes(self):
        for rec in self:
            rec.att_hp, rec.att_atk, rec.att_def, rec.att_spd, rec.att_crit_rate, rec.att_crit_dmg, *_ = rec.attribute_ids
    
    @api.model_create_multi
    def create(self, vals_list):
        characters = super(Character, self).create(vals_list)
        for ch in characters:
            # Link character record to character template
            ch.template_id = self.env['sr.character.template'].browse_sr_id([ch.item_id])
        return characters
    
    def generate_character_data(self, data):
        '''
        Create or update character records with given data.
        Linked records will be generated from data and linked to character:
            attribute_ids
            light_cone_id
        :param data: List of character dictionary data
        '''
        self._prepare_api_values(data)
        LightCone = self.env['sr.light.cone']
        for ch in data:
            light_cone_data = LightCone._prepare_api_values(ch.pop('light_cone'))

            # Check if character record exists
            ch_rec = self.browse_sr_id([ch['item_id']])
            if not ch_rec:
                # Create light cone
                ch['light_cone_id'] = LightCone.create(light_cone_data).id
                # Create new character
                self.create(ch)
                _logger.info(f"New character record: {ch['name']}")
            else:
                # Update light cone
                ch_rec.light_cone_id.write(light_cone_data)
                # Update character record
                ch_rec.write(ch)
                _logger.info(f"Updated {ch_rec.name} data.")
            
    def _prepare_api_values(self, data):
        '''
        Method receives list of characters to create sr.character records.
            id          - Object ID, str
            name        - Name of character, str
            rarity      - Star rarity, int
            rank        - Eidolon Level, int
            level       - Character Level, int
            promotion   - Ascension Level, int
            icon        - Icon Image Path, str
            preview     - Preview Image Path, str
            portrait    - Portrait Image Path, str
            rank_icons  - Eidolon Image Paths, list(str)
            path        - Aeon Path, dict
            element     - Element Type, dict
            skills      - Skill Info, list(dict)
            skill_trees - Skill Hierarchy, list(dict)
            light_cone  - Light Cone Equipped, dict
            relics      - Relics Equipped, list(dict)
            relic_sets  - Relic Set Bonuses, list(dict)
            attributes  - Base Attributes, list(dict)
            additions   - Added Attributes, list(dict)
            properties  - Special Passive Bonuses, list(dict)
            pos         - Position in Profile, list(int)
        :param data: List of character dictionaries from json
        :returns: Parsed list of character dictionaries
        '''
        # Remove unused api vals
        to_remove = [
            'rank_icons', # Eidolon ability icons
            # Path & element already in assets
            'path',
            'element',
            'skills', # Skill info
            'skill_trees', # Hierarchy of traces
            # TODO implement these later
            'relics',
            'relic_sets',
            'properties', # Special statistics and passives
            'pos', # Position in profile
        ]
        base_path = '/hsr_warp/static/'

        for ch in data:
            for k in to_remove:
                # Will only remove key if exists
                ch.pop(k, None)
            
            # Rename id key to db friendly, cast to int for lookup
            ch['item_id'] = int(ch.pop('id'))
            # Typecast fields for easy storing
            ch['rarity'] = str(ch.pop('rarity'))
            # Add base path to img paths
            ch['icon_path'] = base_path + ch.pop('icon')
            ch['preview_path'] = base_path + ch.pop('preview')
            ch['portrait_path'] = base_path + ch.pop('portrait')
            # Get attribute commands
            ch['attribute_ids'] = self.env['sr.attribute']._populate_attributes(ch.pop('attributes'), ch.pop('additions'))
        return data