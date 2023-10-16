from odoo import api, fields, models, tools, Command
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
    banner_id = fields.Many2one('sr.banner', store=True, readonly=True, compute='_compute_warp_banner')
    banner_type_id = fields.Many2one('sr.banner.type', store=True, readonly=True, compute='_compute_warp_banner_type')

    _sql_constraints = [
        ('warp_key', 'UNIQUE (wid)',  'You can not have two warps with the same ID')
    ]

    @api.depends('gacha_id')
    def _compute_warp_banner(self):
        for warp in self:
            # # warp.banner_id = None
            # # warp.banner_type_id = None
            # if not self.env['sr.banner']._get_by_gacha_id(warp.gacha_id):
            #     self.env.cr.execute(f"""INSERT INTO sr_banner(name, banner_key, gacha_type_id, active)
            #                         VALUES('~', '{warp.gacha_id}', {warp.gacha_type}, TRUE)""")
            #     # sr_banner = self.env['sr.banner'].create({
            #     #     'banner_key': warp.gacha_id,
            #     #     'gacha_type_id': warp.gacha_type,
            #     # })
            #     self.env.cr.commit()
            #     self.env.cr.execute(f"""UPDATE sr_warp
            #                         SET banner_id = {self.env['sr.banner']._get_by_gacha_id(warp.gacha_id).id}
            #                         WHERE id = {warp.id}""")
            # else:
            warp.banner_id = self.env['sr.banner']._get_by_gacha_id(warp.gacha_id)
        
    @api.depends('gacha_type')
    def _compute_warp_banner_type(self):
        for warp in self:
            warp.banner_type_id = self.env['sr.banner.type'].search([('gacha_type','=',warp.gacha_type)])

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
    active = fields.Boolean('Active', default=True)
    gacha_type = fields.Char('Banner Type', readonly=True)
    warp_ids = fields.One2many('sr.warp', 'banner_type_id', string='Warps')

    pity_level = fields.Integer('Pity', store=True, compute="_compute_warps")
    last_warp = fields.Many2one('sr.warp', string='Last Warp', store=True, compute='_compute_warps')
    last_five_star = fields.Many2one('sr.warp', string='Last 5* Warp', store=True, compute='_compute_warps')

    @api.depends('warp_ids')
    def _compute_warps(self):
        for banner in self:
            if not banner.warp_ids:
                # If no warps
                banner.last_warp = None
                banner.last_five_star = None
                banner.pity_level = 0
                return
            
            banner.last_warp = banner.warp_ids[0]
            # Get all 5* warps
            fives = banner.warp_ids.filtered(lambda w: w.rank_type == 5)
            if fives:
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
    active = fields.Boolean('Active', default=True)
    banner_key = fields.Char('Banner ID', readonly=True)
    gacha_type_id = fields.Many2one('sr.banner.type')

    _sql_constraints = [
        ('banner_key', 'UNIQUE (banner_key)',  'You can not have two banners with the same key')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        return super(Banner, self).create(vals_list)
    
    def _get_by_gacha_id(self, gacha_id):
        self.env.cr.execute(f"SELECT id FROM sr_banner WHERE banner_key = '{gacha_id}'")
        return self.browse(self.env.cr.fetchone())
    
    def generate_banners(self, json_data):
        banners = set()
        for warp in json_data:
            banners.add((warp['gacha_id'], warp['gacha_type']))
        
        for banner in banners:
            if not self._get_by_gacha_id(banner[0]):
                # If we don't have this banner yet
                self.create({'banner_key': banner[0], 'gacha_type_id': banner[1]})
