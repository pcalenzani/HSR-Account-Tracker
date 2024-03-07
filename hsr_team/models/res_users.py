from odoo import api, fields, models, tools, Command
import requests
import logging

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    def get_profile_data(self):
        if not self.sr_uid:
            return
        url = "https://api.mihomo.me/sr_info_parsed/%s?lang=en&version=v2"%(self.sr_uid)
        response = requests.get(url)

        _logger.info("\"GET /sr_info_parsed\" " + str(response.status_code))
        if response.status_code == 200:
            self.env['sr.character'].generate_character_data(response.json()['characters'])
        else:
            _logger.info(url)
            _logger.error(response.reason)
            return