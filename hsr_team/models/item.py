from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class Item(models.Model):
    _name = 'sr.item'
    _description = 'Item'
    _order = 'item_id DESC'
    _inherit = 'sr.image.mixin'

    item_id = fields.Integer('Item ID')
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

    def browse_sr_id(self, sr_ids=None):
        if not sr_ids:
            sr_ids= ()
        elif sr_ids.__class__ is int:
            sr_ids = (sr_ids,)
        else:
            sr_ids= tuple(sr_ids)

        try:
            self.env.cr.execute("""SELECT id FROM sr_character WHERE item_id in %s LIMIT 1""", [sr_ids])
            ids = self.env.cr.fetchall()[0]
        except IndexError:
            return self
        return self.__class__(self.env, ids, ids)


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
            rec.img_id = self.get_image_from_path(img_path, rec.item_id).id

