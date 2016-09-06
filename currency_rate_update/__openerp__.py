# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Currency Rate Update",
    "version": "1.0",
    'summary': 'Currency Rate Update',
    'sequence': 30,
    'description': """
Tipo de cambio para solventar obligaciones denominadas en dólares de los EE.UU.A., pagaderas en la República Mexicana.
------------------------------------------------------
    """,
    "author": "OpenBIAS S.A.",
    "website": "www.bias.com.mx",
    "category": "Financial Management/Configuration",
    "depends": [],
    "data": [
        "views/service_cron_data.xml",
    ],
    "demo": [],
    'external_dependencies': 
        {
            'python' : ['feedparser']
        },
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: