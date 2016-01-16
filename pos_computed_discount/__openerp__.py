# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    'name': 'POS Computed Discount',
    'version': '0.1',
    'author': 'HacBee UAB',
    'category': 'Point Of Sale',
    'website': 'https://www.hbee.eu',
    'description': """
        Adds realtime discount computation to POS.
        Adds seller pop-up for each chosen product.
        Updates POS report to group by sellers.
    """,
    'depends': [
        'hr',
        'point_of_sale',
    ],
    'data': [
        'view/pos.xml',
        'view/hr.xml',
        'view/account.xml',
        'report/pos_order_report.xml',
    ],
    'css': [
        'static/src/css/pos.css'
    ],
    'js': [
        'static/src/js/pos.js',
    ],
    'qweb': [
        'static/src/xml/pos.xml'
    ],
    'installable': True,
    'application': False,
}
