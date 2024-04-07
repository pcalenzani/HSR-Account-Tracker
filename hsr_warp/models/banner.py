from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class BannerType(models.Model):
    _name = 'sr.banner.type'
    _description = 'Warp Banner Type'

    name = fields.Char('Name')
    gacha_type = fields.Char('Gacha Type', readonly=True)
    warp_ids = fields.One2many('sr.warp', 'banner_type_id', string='Warps')

    pity_level = fields.Integer('Pity', store=True, compute='_compute_warps')
    last_warp = fields.Many2one('sr.warp', string='Last Warp', store=True, compute='_compute_warps')
    last_five_star = fields.Many2one('sr.warp', string='Last 5* Warp', store=True, compute='_compute_warps')

    def _get_by_gacha_type_id(self, gacha_type_id):
        return self.search([('gacha_type','=',gacha_type_id)])
    
    @api.depends('warp_ids')
    def _compute_warps(self):
        for banner in self:
            if not banner.warp_ids:
                # If no warps
                banner.last_warp = None
                banner.last_five_star = None
                banner.pity_level = 0
                continue
            
            banner.last_warp = banner.warp_ids[0]
            # Get all 5* warps
            if fives := banner.warp_ids.filtered(lambda w: w.rank_type == 5):
                # Calculate from latest 5*
                banner.last_five_star = fives[0]
                banner.pity_level = len(banner.warp_ids.filtered(lambda w: w.wid > fives[0].wid))
            else:
                # Keep to 0 if no 5* pulls
                banner.last_five_star = None
                banner.pity_level = 0


class Banner(models.Model):
    _name = 'sr.banner'
    _description = 'Warp Banner'

    name = fields.Char('Name', default='~')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    banner_key = fields.Char('Banner ID', index=True)
    gacha_type_id = fields.Many2one('sr.banner.type')

    _sql_constraints = [
        ('banner_key', 'UNIQUE (banner_key)',  'You can not have two banners with the same key')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'gacha_type_id' in vals:
                vals['gacha_type_id'] = self.env['sr.banner.type']._get_by_gacha_type_id(vals['gacha_type_id']).id
        return super(Banner, self).create(vals_list)
    
    def _get_by_gacha_id(self, gacha_id):
        return self.search([('banner_key','=',gacha_id)])
    
    def generate_banners(self, data, fields=None):
        gacha_id, gacha_type = fields or ('gacha_id', 'gacha_type')
        banners = set()
        for warp in data:
            # Store as immutable tuple (gacha_id, gacha_type)
            banners.add((warp[gacha_id], int(warp[gacha_type])))
        
        for banner in banners:
            if not self._get_by_gacha_id(banner[0]):
                # If we don't have this banner yet
                self.create({'banner_key': banner[0], 'gacha_type_id': banner[1]})
