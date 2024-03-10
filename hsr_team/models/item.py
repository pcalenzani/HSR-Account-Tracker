from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class Item(models.Model):
    _name = 'sr.item'
    _description = 'Item'
    _order = 'item_id DESC'
    _inherit = 'sr.image.mixin'

    item_id = fields.Integer('Item ID', index=True)
    name = fields.Char('Name')
    rarity = fields.Selection(selection=[
        ('0', 'N/A'),
        ('1', 'N/A'),
        ('2', '2 Star'),
        ('3', '3 Star'),
        ('4', '4 Star'),
        ('5', '5 Star'),
    ],
    string='Rarity')
    level = fields.Integer('Relic Level')

    def browse_sr_id(self, sr_ids):
        '''
        :params sr_ids: List of ids to search in item_id
        '''
        return self.search([('item_id','in',sr_ids)])


class Material(models.Model):
    _name = 'sr.item.material'
    _description = 'Upgrade Material'
    _inherit = 'sr.item'

    full_name = fields.Char('Full Name')
    type = fields.Selection(
        selection=[
            ('basic', 'General'),
            ('eow', 'Advanced'),
            ('ascension', 'Ascension')
        ]
    )
    img_id = fields.Many2one('ir.attachment', string='Image', compute='_compute_img_id',
                             domain="[('res_model','=','sr.item.material'),('res_field','=','img_id')]")

    @api.depends('item_id')
    def _compute_img_id(self):
        # Get image attachment when updating item_id
        img_path = '/hsr_warp/static/icon/item/'
        for rec in self:
            rec.img_id = rec.get_image_from_path(img_path, rec.item_id).id

