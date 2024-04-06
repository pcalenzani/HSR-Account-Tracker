from odoo import api, fields, models
import requests
import logging

_logger = logging.getLogger(__name__)


class Character(models.Model):
    _name = 'sr.character'
    _description = 'Character'
    _inherit = 'sr.item'
    _order = 'item_id DESC'

    promotion = fields.Integer(string='Ascension Level')
    rank = fields.Integer('Eidolon Level')
    light_cone_id = fields.Many2one('sr.light.cone')
    light_cone_img_id = fields.Many2one(related='light_cone_id.preview_img_id', string='Light Cone Image')
    last_sync = fields.Datetime('Last Sync Date')
    
    # --- Template Fields ---
    template_id = fields.Many2one('sr.character.template')
    count = fields.Integer(related='template_id.count')
    date_obtained = fields.Date(related='template_id.date_obtained')
    free_pulls = fields.Integer(related='template_id.free_pulls')
    warp_ids = fields.One2many(related='template_id.warp_ids')
    eidolon_ids = fields.One2many(related='template_id.eidolon_ids')

    element_id = fields.Many2one(related='template_id.element_id')
    element_img_id = fields.Many2one(related='template_id.element_id.img_id', string='Element Image')
    path_id = fields.Many2one(related='template_id.path_id')
    path_img_id = fields.Many2one(related='template_id.path_id.img_id', string='Path Image')

    general_mat_id = fields.Many2one(related='template_id.general_mat_id')
    general_mat_img_id = fields.Many2one(related='template_id.general_mat_id.img_id', string='General Mat Image')
    skill_mat_id = fields.Many2one(related='template_id.skill_mat_id')
    skill_mat_img_id = fields.Many2one(related='template_id.skill_mat_id.img_id', string='Traces Mat Image')
    advanced_mat_id = fields.Many2one(related='template_id.advanced_mat_id')
    advanced_mat_img_id = fields.Many2one(related='template_id.advanced_mat_id.img_id', string='Advanced Mat Image')
    ascension_mat_id = fields.Many2one(related='template_id.ascension_mat_id')
    ascension_mat_img_id = fields.Many2one(related='template_id.ascension_mat_id.img_id', string='Ascension Mat Image')

    # --- Image Fields ---
    portrait_path = fields.Char('Portrait Image Path')
    preview_path = fields.Char('Preview Image Path')
    icon_path = fields.Char('Icon Image Path')
    portrait_img_id = fields.Many2one('ir.attachment', string='Portrait Image', compute='_compute_images')
    preview_img_id = fields.Many2one('ir.attachment', string='Preview Image', compute='_compute_images')
    icon_img_id = fields.Many2one('ir.attachment', string='Icon Image', compute='_compute_images')

    # --- Stat Fields ---
    attribute_ids = fields.One2many('sr.attribute', 'character_id', string='Character Stats', inverse='_set_attributes')
    att_hp = fields.Many2one('sr.attribute', string='HP Stat', compute='_set_attributes')
    att_atk = fields.Many2one('sr.attribute', string='ATK Stat', compute='_set_attributes')
    att_def = fields.Many2one('sr.attribute', string='DEF Stat', compute='_set_attributes')
    att_spd = fields.Many2one('sr.attribute', string='SPD Stat', compute='_set_attributes')
    att_crit_rate = fields.Many2one('sr.attribute', string='CRIT_RATE Stat', compute='_set_attributes')
    att_crit_dmg = fields.Many2one('sr.attribute', string='CRIT_DMG Stat', compute='_set_attributes')

    # -- Relic Fields ---
    relic_ids = fields.One2many('sr.relic', 'character_id', string='Equipped Relics')
    relic_score = fields.Float('Relic Score')
    
    _sql_constraints = [
        ('character_key', 'UNIQUE (item_id)',  'Duplicate character deteced. Item ID must be unique.')
    ]

    def _compute_display_name(self):
        for rec in self:
            if rec.rank > 0:
                rec.display_name = f"{rec.name} ({rec.rank})"
            else:
                rec.display_name = rec.name

    @api.depends('icon_path', 'preview_path', 'portrait_path')
    def _compute_images(self):
        for rec in self:
            rec.portrait_img_id = rec.get_image_from_path(rec.portrait_path, field='portrait_img_id').id
            rec.preview_img_id = rec.get_image_from_path(rec.preview_path, field='preview_img_id').id
            rec.icon_img_id = rec.get_image_from_path(rec.icon_path, field='icon_img_id').id

    @api.depends('attribute_ids')
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
    
    def calculate_relic_scores(self):
        for character in self:
            character.relic_ids.compute_relic_score()
            character.relic_score = sum(character.relic_ids.mapped('score'))

    def action_calculate_all_scores(self):
        self.search([]).calculate_relic_scores()

    def update_character_data(self, sr_uid=None):
        if not sr_uid and not (sr_uid := self.env.user.sr_uid):
            return
            
        url = "https://api.mihomo.me/sr_info_parsed/%s?lang=en&version=v2"%(sr_uid)
        response = requests.get(url)
        _logger.info("\"GET /sr_info_parsed\" " + str(response.status_code))
        if response.status_code == 200:
            self.generate_character_data(response.json()['characters'])
        else:
            _logger.info(url)
            _logger.error(response.reason)
            return

    def generate_character_data(self, data):
        '''
        Create or update character records with given data.
        Linked records will be generated from data and linked to character:
            attribute_ids
            light_cone_id
        :param data: List of character dictionary data
        :param characters: List of character name strings
        '''
        data = self._prune_character_data(data)
        self._prepare_api_values(data)
        LightCone = self.env['sr.light.cone']
        for ch in data:
            ch['last_sync'] = fields.Datetime.now()
            light_cone_data = LightCone._prepare_api_values(ch.pop('light_cone'))

            # Check if character record exists
            if not (ch_rec := self.browse_sr_id([ch['item_id']])):
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

    def _prune_character_data(self, data):
        if characters := self.env.context.get('character_id'):
            data.filter(lambda x: x.get('name') in characters, data)
        return data
            
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
            # Path & element already in template
            'path',
            'element',
            'skills', # Skill info
            'skill_trees', # Hierarchy of traces
            'relic_sets', # Relic set bonuses
            'properties', # Special statistics and passives
            'pos', # Position in profile
        ]
        base_path = '/hsr_warp/static/'
        Attribute = self.env['sr.attribute']
        Relic = self.env['sr.relic']

        for ch in data:
            # Remove key if exists
            for k in to_remove: ch.pop(k, None) 
            # Rename id key to db friendly, cast to int for lookup
            ch['item_id'] = int(ch.pop('id'))
            # Typecast fields for easy storing
            ch['rarity'] = str(ch.pop('rarity'))
            # Add base path to img paths
            ch['icon_path'] = base_path + ch.pop('icon')
            ch['preview_path'] = base_path + ch.pop('preview')
            ch['portrait_path'] = base_path + ch.pop('portrait')
            # Get attribute commands list
            ch['attribute_ids'] = Attribute._populate_attributes(ch.pop('attributes'), ch.pop('additions'))
            # Get relic commands list
            ch['relic_ids'] = Relic._populate_relics(ch.pop('relics'))
        return data