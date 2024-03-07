from odoo import api, fields, models, tools, Command
import logging

_logger = logging.getLogger(__name__)

class Character(models.Model):
    _name = 'sr.character'
    _description = 'Character'
    _inherit = 'sr.item'
    _order = 'item_id DESC'

    # --- Template Fields ---
    template_id = fields.Many2one('sr.character.template')
    general_mat_id = fields.Many2one(related='template_id.general_mat_id')
    general_mat_img_id = fields.Many2one(related='template_id.general_mat_id.img_id', string='General Material Image')
    advanced_mat_id = fields.Many2one(related='template_id.advanced_mat_id')
    advanced_mat_img_id = fields.Many2one(related='template_id.advanced_mat_id.img_id', string='Advanced Material Image')
    ascension_mat_id = fields.Many2one(related='template_id.ascension_mat_id')
    ascension_mat_img_id = fields.Many2one(related='template_id.ascension_mat_id.img_id', string='Ascension Material Image')
    eidolon_ids = fields.One2many(related='template_id.eidolon_ids')
    element_id = fields.Many2one(related='template_id.element_id')
    element_img_id = fields.Many2one(related='template_id.element_id.img_id')
    path_id = fields.Many2one(related='template_id.path_id')
    path_img_id = fields.Many2one(related='template_id.path_id.img_id')
    portrait_img_id = fields.Many2one(related='template_id.portrait_img_id')
    preview_img_id = fields.Many2one(related='template_id.preview_img_id')
    icon_img_id = fields.Many2one(related='template_id.icon_img_id')

    # --- Manual Fields ---
    count = fields.Integer('Count', store=True, compute='_compute_count')
    is_owned = fields.Boolean('Is Owned', store=True, compute='_compute_count')
    date_obtained = fields.Date('Obtained on')
    free_pulls = fields.Integer('Free Pulls')

    # --- API Fields ---
    promotion = fields.Integer(string='Ascension Level')
    light_cone_id = fields.Many2one('sr.light.cone')
    
    rank = fields.Integer('Eidolon Level')
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
    
    @api.model_create_multi
    def create(self, vals_list):
        characters = super(Character, self).create(vals_list)
        for ch in characters:
            # Link character record to character template
            ch.template_id = self.env['sr.character.template'].browse_sr_id(ch.item_id)
            _logger.info(f"New character record: {ch.name}")
        
        return characters
    
    def generate_character_data(self, data):
        self._prepare_character_values(data)
        for ch in data:
            # Check if character record exists
            ch_rec = self.browse_sr_id(ch['item_id'])
            if not ch_rec:
                # Create new item
                self.create(ch)
            else:
                # Update item
                ch_rec.write(ch)
                _logger.info(f"Updated {ch_rec.name} data.")
            
    def _prepare_character_values(self, ch_data):
        '''
        Method receives list of characters to create sr.character records.
        :param ch_data: List of character dictionaries from json
        :returns: Parsed list of character dictionaries
        '''
        # Remove unused api vals
        to_remove = [
            # Character images already set up in assets
            'icon',
            'preview',
            'portrait',
            'rank_icons', # Eidolon ability icons
            # Character data/icons already in assets
            'path',
            'element',
            'skills', # Skill info
            'skill_trees', # Hierarchy of traces
            # TODO implement these later
            'light_cone',
            'relics',
            'relic_sets',
            'attributes', # Character base statistics
            'additions', # Character added statistics
            'properties', # Special statistics and passives
            'pos', # Position in profile
        ]

        for ch in ch_data:
            for k in to_remove:
                # Will only remove key if exists
                ch.pop(k, None)
            
            # Rename id key to db friendly, cast to int for lookup
            ch['item_id'] = int(ch.pop('id'))
            # Typecast fields for easy storing
            ch['rarity'] = str(ch.pop('rarity'))
        return ch_data