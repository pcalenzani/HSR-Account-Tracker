from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class LightCone(models.Model):
    _name = 'sr.light.cone'
    _description = 'Light Cone'
    _inherit = 'sr.item'
    _order = 'item_id DESC'

    rank = fields.Integer('Rank')
    promotion = fields.Integer('Superimposition')

    path_id = fields.Many2one('sr.path', string='Path')
