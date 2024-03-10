from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class LightCone(models.Model):
    _name = 'sr.light.cone'
    _description = 'Light Cone'
    _inherit = 'sr.item'
    _order = 'item_id DESC'

    rank = fields.Integer('Superimposition')
    promotion = fields.Integer('Ascension Level')

    portrait_path = fields.Char('Portrait Image Path')
    preview_path = fields.Char('Preview Image Path')
    icon_path = fields.Char('Icon Image Path')
    portrait_img_id = fields.Many2one('ir.attachment', string='Portrait Image', compute='_compute_images')
    preview_img_id = fields.Many2one('ir.attachment', string='Preview Image', compute='_compute_images')
    icon_img_id = fields.Many2one('ir.attachment', string='Icon Image', compute='_compute_images')

    path_id = fields.Many2one('sr.path', string='Path')
    character_ids = fields.One2many('sr.character', 'light_cone_id', string='Character Link')
    character_id = fields.Many2one('sr.character', string='Equipped By', store=True, compute='_compute_character_id', ondelete='cascade')

    attribute_ids = fields.One2many('sr.attribute', 'light_cone_id', string='Light Cone Stats', inverse='_set_attributes')
    att_hp = fields.Many2one('sr.attribute', string='HP Stat')
    att_atk = fields.Many2one('sr.attribute', string='ATK Stat')
    att_def = fields.Many2one('sr.attribute', string='DEF Stat')

    @api.depends('icon_path', 'preview_path', 'portrait_path')
    def _compute_images(self):
        for rec in self:
            rec.portrait_img_id = rec.get_image_from_path(rec.portrait_path, field='portrait_img_id').id
            rec.preview_img_id = rec.get_image_from_path(rec.preview_path, field='preview_img_id').id
            rec.icon_img_id = rec.get_image_from_path(rec.icon_path, field='icon_img_id').id

    @api.depends('character_ids')
    def _compute_character_id(self):
        for rec in self:
            # Should not have more than one in o2m field, only used to simulate o2o link
            rec.character_id = rec.character_ids
            
    def _set_attributes(self):
        for rec in self:
            rec.att_hp, rec.att_atk, rec.att_def = rec.attribute_ids

    def _prepare_api_values(self, data):
        '''
        Method receives light cone data and returns sanitized dict
            id          - Object ID, str
            name        - Name of Light Cone, str
            rarity      - Star Rarity, int
            rank        - Superimposition Level, int
            level       - Light Cone Level, int
            promotion   - Ascension Level, int
            icon        - Icon Image Path, str
            preview     - Preview Image Path, str
            portrait    - Portrait Image Path, str
            path        - Aeon Path, dict
            attributes  - Stat Attributes, list(dict)
            properties  - Special Passive Bonuses, list(dict)
        :param data: Dictionary of light cone from json
        :returns: Parsed dict of light cone values
        '''
        # Remove unused api vals
        to_remove = ['properties']
        base_path = '/hsr_warp/static/'

        for k in to_remove:
            # Will only remove key if exists
            data.pop(k, None)

        # Rename id key to db friendly, cast to int for lookup
        data['item_id'] = int(data.pop('id'))
        # Typecast fields for easy storing
        data['rarity'] = str(data.pop('rarity'))
        # Get path record
        data['path_id'] = self.env['sr.path'].search([('reference','=',data.pop('path')['id'])]).id
        # Add base path to img paths
        data['icon_path'] = base_path + data.pop('icon')
        data['preview_path'] = base_path + data.pop('preview')
        data['portrait_path'] = base_path + data.pop('portrait')
        # Prepare command list for attributes
        data['attribute_ids'] = self.env['sr.attribute']._populate_attributes(data.pop('attributes'))
        return data

    # TODO: Add images, implement m2o links