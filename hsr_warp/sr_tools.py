import base64

from odoo import tools
from odoo.modules import get_module_resource

def _read_image(path):
    if not path:
        return False
    path_info = path.split(',')
    icon_path = get_module_resource(path_info[0], path_info[1])
    image = False
    if icon_path:
        with tools.file_open(icon_path, 'rb') as icon_file:
            image = base64.encodebytes(icon_file.read())
    return image

def get_image_data(img_path):
    if img_path and len(img_path.split(',')) == 2:
        return _read_image(img_path)
    