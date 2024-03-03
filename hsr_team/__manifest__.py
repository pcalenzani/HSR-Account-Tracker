{
    'name': 'Character Tracker',
    'version': '1.0',
    'summary': 'Honkai: Star Rail - Character Tracker',
    'sequence': 1,
    'description': "",
    'depends': ['hsr_warp'],
    'data': [
        'views/hsr_team_menu_items.xml'
        'views/hsr_team_character_views.xml',
        'views/hsr_team_item_views.xml',
        'views/hsr_team_character_type_views.xml',

        'data/sr_material_data.xml',
        'data/sr_element_path_data.xml',
        'data/sr_character_data.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'icon': '/hsr_warp/static/description/icon(3).jpg',
    'pre_init_hook': 'pre_init',
    'assets': {}
}