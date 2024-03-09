from odoo import models
import logging

_logger = logging.getLogger(__name__)

# -- Abstract model for image creation --

class ImageMixin(models.AbstractModel):
    _name = 'sr.image.mixin'
    _description = 'Abstract Image Model'
    

    def generate_image(self, path, name, field=None):
        if not name:
            # Use the item_id field if file name isn't passed in
            name = self.item_id
        name = str(name) + '.png'
        if not field:
            # Use standard img field name if none passed in
            field = 'img_id'

        # ! Can't use Command because field is not M2M
        return self.env['ir.attachment'].create({
                    'name': name,
                    'res_model': self._name,
                    'res_field': field,
                    'public': True,
                    'type': 'url',
                    'url': path + name
                })

