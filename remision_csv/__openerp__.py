# -*- encoding: utf-8 -*-

 
{
    'name' : 'Export Remision CSV',
    'version' : '1.0',
    'author' : 'silvau',
    'website' : 'http://www.zeval.com.mx',
    'category' : '',
    'depends' : ['stock'],
    'description': """
    Genera un archivo csv a partir de la remision de entrada
    """,
    'data': [
        'wizard/download_csv_view.xml',
        'wizard/download_csv_view_internal.xml',
        'views/stock_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
