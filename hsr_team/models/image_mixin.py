from odoo import api, fields, models, tools, Command
from odoo.modules import get_module_resource
import logging
import base64

_logger = logging.getLogger(__name__)

# -- Abstrace model for image compute functions --

class ImageMixin(models.AbstractModel):
    _name = 'sr.image.mixin'
    _description = 'Abstract Image Model'
        
    def _read_image(self, module, path):
        icon_path = get_module_resource(module, path)
        image = False
        
        if icon_path:
            with tools.file_open(icon_path, 'rb') as icon_file:
                image = base64.encodebytes(icon_file.read())
        else:
            _logger.error(path)
        return image

    def get_image_data(self, img_path):
        if img_path:
            return self._read_image('hsr_warp', 'static/' +  img_path)