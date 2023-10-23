{
    'name': 'Warp Tracker',
    'version': '1.0',
    'summary': 'Honkai: Star Rail - Warp Tracker',
    'sequence': 0,
    'description': "",
    'depends': ['base'],
    'data': [
        'data/sr_banner_data.xml',
        'data/ir_cron_data.xml',
        'views/hsr_warp_warp_views.xml',

        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': ['hsr_warp/static/src/web_client.js']
    },
    'installable': True,
    'application': True,
    'icon': '/hsr_warp/static/description/icon(1).jpg',
    # 'post_init_hook': '_method_name',
    'assets': {}
}