# -*- encoding: utf-8 -*-

{
    'name' : 'Filters for lot tree view',
    'version' : '1.0',
    'author' : 'silvau',
    'website' : 'http://www.zeval.com.mx',
    'category' : 'Views',
    'depends' : ['stock'],
    'description': """
    Adds a filter to show the lots of products with a selected category only 
    """,
    'data': [
        'views/production_lot_view.xml',
    ],
    'installable': True,
    'auto_install': False,

}
