# -*- encoding: utf-8 -*-

{
    'name' : 'Existence by warehouse in lots',
    'version' : '1.0',
    'author' : 'silvau',
    'website' : 'http://www.zeval.com.mx',
    'category' : 'Stock',
    'depends' : ['stock','mrp','users_warehouse'],
    'description': """
    Adds a page to form view on lots to calculate the existence by warehouse
    """,
    'init_xml': [
        'security/ir.model.access.csv',
    ],

    'data': [
        'views/lot_existence.xml',
        'views/production_lot_view.xml',
        'views/init_hook.xml',
    ],
    'external_dependencies': {
        'python' : ['pandas'],
    },
    'installable': True,
    'auto_install': False,

}
