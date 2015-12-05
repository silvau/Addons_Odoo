# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    'name': 'POS Show Default Code',
    'version': '0.1',
    'author': 'silvau',
    'category': 'Point Of Sale',
    'website': 'https://www.zenpar.com.mx',
    'description': """
        Show default code in product list of POS
    """,
    'depends': [
        'point_of_sale',
    ],
    'data': [
    ],
    'css': [
    ],
    'js': [
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
    'application': False,
}
