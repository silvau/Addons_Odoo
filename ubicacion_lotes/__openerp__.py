# -*- coding: utf-8 -*-
# © <2016> <silvau>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Ubicacion en lotes",
    "summary": "Agrega un campo de ubicacion de lote.",
    "version": "1.0.1.0.0",
    "category": "stock",
    "website": "http://zeval.com.mx/",
    "author": "silvau",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "prodlot_ref_seq",
    ],
    'init_xml': [
        'security/ir.model.access.csv',
    ],

    "data": [
        "views/ubicaciones_view.xml",
    ],
}
