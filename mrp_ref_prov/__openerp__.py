# -*- encoding: utf-8 -*-

 
{
    'name' : 'Reference on PO from MRP repair ',
    'version' : '1.0',
    'author' : 'silvau',
    'website' : 'http://www.zeval.com.mx',
    'category' : '',
    'depends' : ['mrp_repair','mrp_repair_zenpar'],
    'description': """
    Adds a reference for the Purchase Order when created from mrp repair confirmation
    """,
    'data': [
        'views/mrp_repair_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
