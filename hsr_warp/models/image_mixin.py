from odoo import models
import logging

_logger = logging.getLogger(__name__)

# -- Abstract model for image creation --

class ImageMixin(models.AbstractModel):
    _name = 'sr.image.mixin'
    _description = 'Abstract Image Model'
    
    def get_image_from_path(self, path, name, field=None):
        name = str(name) + '.png'
        if not field:
            # Use standard img field name if none passed in
            field = 'img_id'
        
        Attachment = self.env['ir.attachment']
        # ir.attachment will auto filter records that have res_field unless specified
        img_exists = Attachment.search([('res_field','=',field),('url','=',path + name)])
        if img_exists:
            return img_exists

        # ! Can't use Command because field is not M2M
        return Attachment.create({
                    'name': name,
                    'res_model': self._name,
                    'res_field': field,
                    'public': True,
                    'type': 'url',
                    'url': path + name
                })

