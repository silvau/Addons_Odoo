# -*- encoding: utf-8 -*-
 
{
    'name' : 'Warning on sale confirm',
    'version' : '1.0',
    'author' : 'silvau',
    'website' : 'http://www.zeval.com.mx',
    'category' : '',
    'depends' : ['sale', 'stock'],
    'description': """
    Agrega un warning al confirmar la venta. Ofrece seguir con el proceso o cancelar la confirmacion para hacer los cambios pertinentes.
    Esto solo aplica para los productos con el booleano es_papel activado.
    """,
    'data': [
        'views/sale_order_view.xml',
        'wizard/sale_order_wizard.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
