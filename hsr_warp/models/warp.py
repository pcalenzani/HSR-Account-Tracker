from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class Warp(models.Model):
    _name = 'sr.warp'
    _description = 'Warp'
    _order = 'wid desc'
    _inherit = 'sr.image.mixin'

    uid = fields.Char('User ID')
    gacha_id = fields.Char('Gacha ID')
    gacha_type = fields.Char('Gacha Type ID')
    item_id = fields.Char('Item ID')
    count = fields.Char('Count')
    time = fields.Datetime('Time')
    name = fields.Char('Name')
    lang = fields.Char('Lang')
    item_type = fields.Char('Item Type')
    rank_type = fields.Integer('Rarity')
    wid = fields.Char('Warp ID', index=True) # ID is out of int bounds, cannot use long int so need to be char

    pity = fields.Integer('Pity', store=True, compute='_compute_pity')
    banner_id = fields.Many2one('sr.banner', store=True, compute='_compute_banner')
    banner_type_id = fields.Many2one('sr.banner.type', store=True, compute='_compute_banner')
    character_id = fields.Many2one('sr.character.template', store=True, compute='_compute_character_id')
    img_id = fields.Many2one('ir.attachment', string='Image', compute='_compute_img_id')

    _sql_constraints = [
        ('warp_key', 'UNIQUE (wid)',  'You can not have two warps with the same ID')
    ]

    def load(self, fields, data):
        '''
        Method override for importing records
        :param fields: List of fields being imported
        :param data: Matrix of data to be imported
        '''
        if 'gacha_id' not in fields:
            raise UserError('The import file must contain a banner id column.')
        
        fields.append('banner_id.id')
        fields.append('.id')
        wid_index = fields.index('wid')
        gacha_index = fields.index('gacha_id'), fields.index('gacha_type')
        self.env['sr.banner'].generate_banners(data, fields=gacha_index)

        # Prepare banner dict to reference ids
        banner_ids = {}
        banners = self.env['sr.banner'].search_read(domain=[], fields=['banner_key'])
        for banner in banners:
            banner_ids[banner['banner_key']] = banner['id']

        for row in data:
            banner_id = banner_ids.get(row[gacha_index[0]])
            row.append(banner_id)

            # If the warp id is already in db, add id to update record
            if warp := self.browse_sr_id([row[wid_index]]):
                row.append(warp.id)

        return super().load(fields, data)

    @api.depends('gacha_id', 'gacha_type')
    def _compute_banner(self):
        for rec in self:
            rec.banner_id = self.env['sr.banner']._get_by_gacha_id(rec.gacha_id)
            rec.banner_type_id = self.env['sr.banner.type']._get_by_gacha_type_id(rec.gacha_type)

    @api.depends('item_id')
    def _compute_character_id(self):
        for rec in self:
            if rec.item_type == 'Light Cone':
                rec.character_id = None
            elif rec.item_type == 'Character':
                rec.character_id = self.env['sr.character.template'].browse_sr_id([rec.item_id])

    @api.depends('item_id')
    def _compute_img_id(self):
        for rec in self:
            if rec.item_type == 'Light Cone':
                path = '/hsr_warp/static/image/light_cone_preview/'
            elif rec.item_type == 'Character':
                path = '/hsr_warp/static/image/character_preview/'
            rec.img_id = rec.get_image_from_path(path, rec.item_id).id
            
    def _compute_warp_pity(self):
        for rec in self:
            latest_five = self.search([('rank_type','=',5),('banner_type_id','=',rec.banner_type_id),('wid','<',rec.wid)], limit=1, order='wid desc')
            # Get most recent 5* pull, get count of how many warps since that pull
            if latest_five:
                rec.pity = self.search_count([('banner_type_id','=',rec.banner_type_id),('wid','<=',rec.wid),('wid','>',latest_five.wid)])
            else:
                # For the first 5* pull, get count of all warps before
                rec.pity = self.search_count([('banner_type_id','=',rec.banner_type_id),('wid','<=',rec.wid)])
    
    def browse_sr_id(self, sr_ids):
        '''
        :params sr_ids: List of ids to search in wid
        '''
        return self.search([('wid','in',sr_ids)])

    def generate_warps(self, vals_list):
        '''
        Create warp records from given list of values
        :param vals_list: Values list of warp data
        :returns: Oldest warp id used for pagination
        '''
        # Check if warps exist before creating
        for i in range(len(vals_list)):
            id = vals_list[i]['id']
            if self.browse_sr_id([id]):
                _logger.warning("ID FOUND: " + str(id) + " - Skipping...")
                # Truncate vals list when duplicate id found
                vals_list = vals_list[:i]
                break
        if not vals_list:
            # Truncate may have happened at first index, return nothing
            return None
        
        warps = self.create(vals_list)
        _logger.debug(warps)
        return warps[-1]['wid']

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'time' in vals:
                vals['time'] = datetime.strptime(vals['time'], "%Y-%m-%d %H:%M:%S") + timedelta(hours=+5)
            if 'id' in vals:
                vals['wid'] = vals.pop('id')
            if 'gacha_id' in vals:
                vals['banner_id'] = self.env['sr.banner']._get_by_gacha_id(vals['gacha_id']).id
            if 'gacha_type' in vals:
                vals['banner_type_id'] = self.env['sr.banner.type'].search([('gacha_type','=',vals['gacha_type'])]).id
        return super(Warp, self).create(vals_list)

