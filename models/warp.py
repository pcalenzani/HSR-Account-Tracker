from odoo import api, fields, models, tools
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class Warp(models.Model):
    _name = 'sr.warp'
    _description = 'Warp'
    _order = 'wid desc'

    uid = fields.Char('User ID', readonly=True)
    gacha_id = fields.Char('Banner ID', readonly=True)
    gacha_type = fields.Char('Banner Type', readonly=True)
    item_id = fields.Char('Item ID', readonly=True)
    count = fields.Char('Count')
    time = fields.Datetime('Time', readonly=True)
    name = fields.Char('Name')
    lang = fields.Char('Lang')
    item_type = fields.Char('Item Type')
    rank_type = fields.Integer('Rarity')
    wid = fields.Char('Warp ID', index=True, readonly=True)

    pity = fields.Integer("Pity", store=True, _compute_pity="_compute_pity")
    banner_id = fields.Many2one('sr.banner', readonly=True, compute='_compute_warp_banner')
    banner_type_id = fields.Many2one('sr.banner.type', readonly=True, compute='_compute_warp_banner_type')

    _sql_constraints = [
        ('warp_key', 'UNIQUE (wid)',  'You can not have two warps with the same ID')
    ]

    def _compute_warp_banner(self):
        for warp in self:
            sr_banner = self.env['sr.banner'].search([('banner_key','=',warp.gacha_id)])
            if not sr_banner:
                sr_banner = self.env['sr.banner'].create({
                    'banner_key': warp.gacha_id,
                    'gacha_type_id': warp.gacha_type,
                })
            warp.banner_id = sr_banner
        
    def _compute_warp_banner_type(self):
        for warp in self:
            warp.banner_type_id = self.env['sr.banner.type'].search([('gacha_type','=',warp.banner_type_id)])

    def _compute_warp_pity(self):
        for warp in self:
            # TODO calculate pity
            warp.pity = 0

    def _warp_exists(self, wid):
        # Returns 1 if the wid is already recorded
        self.env.cr.execute(f"SELECT 1 FROM sr_warp WHERE wid='{wid}'")
        ret = self.env.cr.fetchone()
        return ret

    def generate_warps(self, vals_list):
        # Check if warps exist before creating
        for i in range(len(vals_list)):
            id = vals_list[i]['id']
            if self._warp_exists(id):
                vals_list = vals_list[:i]
                break

        if not vals_list:
            return None
        
        warps = self.create(vals_list)
        _logger.debug(warps)
        # Return oldest warp for pagination
        return warps[-1]['wid']

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'time' in vals:
                vals['time'] = datetime.strptime(vals['time'], "%Y-%m-%d %H:%M:%S") + timedelta(hours=+5)
            if 'id' in vals:
                vals['wid'] = vals.pop('id')
        
        return super(Warp, self).create(vals_list)



class BannerType(models.Model):
    _name = 'sr.banner.type'
    _description = 'Warp Banner Type'

    name = fields.Char('Name')
    active = fields.Boolean('Active')
    gacha_type = fields.Char('Banner Type', readonly=True)
    pity_level = fields.Integer('Pity', store=False, compute="_compute_pity_level")

    def _compute_pity_level(self):
        for banner in self:
            # TODO calculate pity
            banner.pity_level = 0

class Banner(models.Model):
    _name = 'sr.banner'
    _description = 'Warp Banner'

    name = fields.Char('Name', default='~')
    active = fields.Boolean('Active')
    banner_key = fields.Char('Banner ID', readonly=True)
    gacha_type_id = fields.Many2one('sr.banner.type')

    _sql_constraints = [
        ('banner_key', 'UNIQUE (banner_key)',  'You can not have two banners with the same key')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        return super(Banner, self).create(vals_list)