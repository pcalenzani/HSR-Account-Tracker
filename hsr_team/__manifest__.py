{
    'name': 'HSR: Character Tracker',
    'version': '1.0',
    'summary': 'Honkai: Star Rail - Character Tracker',
    'sequence': 0,
    'description': "",
    'depends': ['hsr_warp'],
    'data': [
        'views/hsr_team_character_views.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'icon': '/hsr_warp/static/description/icon(3).jpg',
    # 'post_init_hook': '_method_name',
    'assets': {}
}