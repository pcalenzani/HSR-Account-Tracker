{
    'name': 'Honkai: Star Rail',
    'version': '1.0',
    'summary': 'Honkai: Star Rail Suite',
    'sequence': 10,
    'description': "",
    'depends': ['base'],
    'data': [
        'data/sr_banner_data.xml',
        'views/starrail_warp_views.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    # 'post_init_hook': '_method_name',
    'assets': {}
}