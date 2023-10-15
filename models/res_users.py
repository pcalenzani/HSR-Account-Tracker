from odoo import api, fields, models, tools
from urllib.parse import urlencode, parse_qs
import requests
import logging

_logger = logging.getLogger(__name__)

WARP_API_URL = 'https://api-os-takumi.mihoyo.com/common/gacha_record/api/getGachaLog'

class Users(models.Model):
    _description = 'Player'
    _inherit = 'res.users'

    sr_uid = fields.Char('Star Rail UID')
    sr_authkey = fields.Char('Auth Key')
    sr_update = fields.Boolean('Update Player Warps', default=False)

    def get_authkey_from_url(self, url):
        self.sr_authkey = parse_qs(url)['authkey']

    def get_warp_data(self, gacha_type, size=20, end_id=0):
        self.ensure_one()

        params = {
            'authkey_ver': '1',
            'lang': 'en',
            'authkey': self.sr_authkey,
            'game_biz': 'hkrpg_global',
            'size': size,
            'gacha_type': gacha_type,
            'end_id': end_id
        }
        url = WARP_API_URL + '?' + urlencode(params)
        ret = requests.get(url).json()
        _logger.debug(url)

        # TODO Log or raise this
        if ret['retcode'] != 0:
            print(f"Error {ret['retcode']}: {ret['message']}") 
        return ret['data']
    
    def get_warps(self):
        banner_types = self.env['sr.banner.type'].search([]).mapped('banner_key')

        for type in banner_types:
            end_id = 0
            while end_id is not None:
                data = self.get_warp_data(type, end_id=end_id)
                if not data or not len(data['list']):
                    break

                end_id = self.env['sr.warp'].generate_warps(data['list'])
