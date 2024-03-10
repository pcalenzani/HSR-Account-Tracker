{
    'name': 'Star Rail Base',
    'version': '1.0',
    'summary': 'Honkai: Star Rail - Warp Tracker',
    'sequence': 0,
    'description': "",
    'depends': ['base', 'web'],
    'data': [
        'data/sr_banner_data.xml',
        'data/ir_cron_data.xml',
        'data/ir_asset.xml',
        'data/sr_element_path_data.xml',
        'data/sr_character_data.xml',

        'views/hsr_warp_menu_items.xml',
        'views/hsr_warp_warp_views.xml',
        'views/hsr_warp_character_type_views.xml',
        'views/hsr_warp_character_template_views.xml',

        'security/ir.model.access.csv',
    ],
    'assets': { # Make ir.asset records
        # 'web.dark_mode_assets_backend': ['hsr_warp/static/src/css/hsr_warp.css'],
        'web.assets_backend': ['hsr_warp/static/src/css/hsr_warp.css',
                               'hsr_warp/static/src/views/attachment_image_field.xml'],
    },
    'installable': True,
    'application': True,
    'icon': '/hsr_warp/static/description/icon(1).png',
    # 'post_init_hook': '_method_name',
    'license': 'LGPL-3',
}