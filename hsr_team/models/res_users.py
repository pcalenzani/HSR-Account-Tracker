from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    def get_profile_data(self):
        if not self.sr_uid:
            return
        self.env['sr.character'].update_character_data(self.sr_uid)