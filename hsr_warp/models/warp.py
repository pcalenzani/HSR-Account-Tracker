from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class Warp(models.Model):
    _name = 'sr.warp'
    _description = 'Warp'
    _order = 'wid desc'

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
    wid = fields.Char('Warp ID', index=True)

    pity = fields.Integer('Pity', store=True, compute='_compute_pity')
    banner_id = fields.Many2one('sr.banner', store=True, compute='_compute_banner_id')
    banner_type_id = fields.Many2one('sr.banner.type', store=True, compute='_compute_banner_type_id')
    character_id = fields.Many2one('sr.character.template', store=True, compute='_compute_character_id')

    _sql_constraints = [
        ('warp_key', 'UNIQUE (wid)',  'You can not have two warps with the same ID')
    ]

    def load(self, fields, data):
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

            warp = self.browse_sr_id(row[wid_index])
            if warp:
                row.append(warp.id)

        return super().load(fields, data)

    @api.depends('gacha_id')
    def _compute_banner_id(self):
        for warp in self:
            warp.banner_id = self.env['sr.banner']._get_by_gacha_id(warp.gacha_id)

    @api.depends('gacha_type')
    def _compute_banner_type_id(self):
        for warp in self:
            warp.banner_type_id = self.env['sr.banner.type'].search([('gacha_type','=',warp.gacha_type)])

    def _compute_warp_pity(self):
        for warp in self:
            # TODO calculate pity
            warp.pity = 0
    
    def _compute_character_id(self):
        for warp in self:
            warp.character_id = self.env['sr.character.template'].search([('character_id','=',warp.item_id)]) or None
            
    def browse_sr_id(self, sr_ids=None):
        if not sr_ids:
            sr_ids= ()
        elif sr_ids.__class__ is int:
            sr_ids = (str(sr_ids),)
        elif sr_ids.__class__ is str:
            sr_ids = (sr_ids,)
        else:
            sr_ids= tuple(sr_ids)

        try:
            self.env.cr.execute("""SELECT id FROM sr_warp WHERE wid in %s LIMIT 1""", [sr_ids])
            ids = self.env.cr.fetchall()[0]
        except IndexError:
            return self
        return self.__class__(self.env, ids, ids)

    def generate_warps(self, vals_list):
        '''
        Create warp records from given list of values
        :param vals_list: Values list of warp data
        :returns: Oldest warp id used for pagination
        '''
        # Check if warps exist before creating
        for i in range(len(vals_list)):
            id = vals_list[i]['id']
            if self.browse_sr_id(id):
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

