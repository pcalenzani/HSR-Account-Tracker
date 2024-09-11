from odoo import api, fields, models, tools
from urllib.parse import urlencode, parse_qs, unquote
import requests
import logging

_logger = logging.getLogger(__name__)

WARP_API_URL = 'https://public-operation-hkrpg-sg.hoyoverse.com/common/gacha_record/api/getGachaLog'

class Users(models.Model):
    _description = 'Player'
    _inherit = 'res.users'

    sr_uid = fields.Char('Star Rail UID')
    sr_authkey = fields.Char('Warp URL')
    sr_update = fields.Boolean('Update Player Warps', default=False)

    def get_authkey_from_url(self):
        authkey_raw = parse_qs(self.sr_authkey)['authkey'][0]
        return unquote(authkey_raw)

    def get_warp_data(self, gacha_type, size=20, end_id=0):
        self.ensure_one()

        params = {
            'authkey_ver': '1',
            'lang': 'en',
            'authkey': self.get_authkey_from_url(),
            'game_biz': 'hkrpg_global',
            'size': size,
            'gacha_type': gacha_type,
            'end_id': end_id
        }
        url = WARP_API_URL + '?' + urlencode(params)
        ret = requests.get(url).json()

        if ret['retcode'] != 0:
            _logger.error(f"Error {ret['retcode']}: {ret['message']}") 
            _logger.error(f"Error from URL: {WARP_API_URL}") 
        return ret['data']
    
    def get_warps(self):
        banner_types = self.env['sr.banner.type'].search([]).mapped('gacha_type')

        for type in banner_types:
            end_id = 0
            while end_id is not None:
                data = self.get_warp_data(type, end_id=end_id)
                if not data or not len(data['list']):
                    break

                self.env['sr.banner'].generate_banners(data['list'])
                end_id = self.env['sr.warp'].generate_warps(data['list'])

    def config_player_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Player Configuration',
            'res_model': 'res.users',
            'res_id': self.env.user.id,
            'target': 'current',
            'view_mode': 'form',
            'view_id': self.env.ref('hsr_warp.hsr_warp_sr_player_view_form').id,
            'context': {'create': False, 'delete': False}
        }

    def _cron_auto_get_warps(self):
        players = self.env['res.users'].search([('sr_update','=',True)])

        for player in players:
            player.get_warps()
