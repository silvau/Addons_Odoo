# -*- coding: utf-8 -*-
{
    "name": "Secuence number for stock picking",
    "description": "This module adds a sequence number to stock picking",
    "version": "7.1",
    "category": "Fields",
    "website": "https://zeval.com.mx/",
    "author": "silvau",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    'init_xml': [
        "views/sequence.xml",
    ],

    "data": [
        "views/stock_picking_view.xml",
    ],
}
