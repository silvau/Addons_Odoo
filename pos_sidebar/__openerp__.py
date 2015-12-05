# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    'name': 'POS Hide Side Bar',
    'version': '0.1',
    'author': 'silvau',
    'category': 'Point Of Sale',
    'website': 'https://www.zenpar.com.mx',
    'description': """
        Hides Side Bar until next order.
    """,
    'depends': [
        'point_of_sale',
    ],
    'data': [
    ],
    'css': [
    ],
    'js': [
        'static/src/js/screens.js',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
