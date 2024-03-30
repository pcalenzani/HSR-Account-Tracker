from os.path import basename
from urllib.parse import urlparse
from odoo import models
import logging

_logger = logging.getLogger(__name__)

# -- Abstract model for image creation --

class ImageMixin(models.AbstractModel):
    _name = 'sr.image.mixin'
    _description = 'Abstract Image Model'
    
    def _get_file_name(self, url):
        # Return name of file from a url path
        return basename(urlparse(url).path)

    def get_image_from_path(self, path, name=None, field=None):
        if not name:
            # Get file name if not passed in params
            name = self._get_file_name(path)
        else:
            # Add png file extension
            name = str(name) + '.png'
            # Update path with full path string
            path += name

        if not field:
            # Use standard img field name if none passed in
            field = 'img_id'
        
        Attachment = self.env['ir.attachment']
        # ir.attachment will auto filter records that have res_field unless specified
        if img_exists := Attachment.search([('res_field','=',field),('url','=',path)]):
            # Return existing attachment record if found
            return img_exists

        # ! Can't use Command because field is not M2M
        return Attachment.create({
                    'name': name,
                    'res_model': self._name,
                    'res_field': field,
                    'public': True,
                    'type': 'url',
                    'url': path
                })

