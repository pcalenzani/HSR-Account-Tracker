from odoo import api, fields, models, tools
from urllib.parse import urlencode, parse_qs
import requests

WARP_API_URL = "https://api-os-takumi.mihoyo.com/common/gacha_record/api/getGachaLog"

class Users(models.Model):
    _name = "sr.warp"
    _description = "Warp"
    _inherit = "res.users"

    sr_uid = fields.Char(string="Star Rail UID")
    sr_authkey = fields.Char(string="Auth Key")

def getAuthKeyFromUrl(self, url):
    self.sr_authkey = parse_qs(url)["authkey"]

def getWarpData(self, gacha_type):
    params = {
        'authkey_ver': '1',
        'lang': 'en',
        'authkey': self.sr_authkey,
        'game_biz': 'hkrpg_global',
        'size': '20',
        'gacha_type': gacha_type,
        'end_id': '0' # TODO
    }
    return requests.get(WARP_API_URL + "?" + urlencode(params)).json()

