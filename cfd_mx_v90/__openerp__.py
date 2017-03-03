# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name' : 'Factura Electronica Mexico',
    'version' : '2.7',
    'summary': 'Factura Electronica Mexico',
    'sequence': 100,
    'description': """
Modulo para generar los xml de la factura electronica
==================================

Descuentos: Para hacer un cfdi con descuento, hay que poner una partida extra con la cantidad negativa. 
------------------------------------------------------
Ejemplo: 
Para poner un descuento de $100, poner una partida cuyo precio sea -100. La partida debe tener impuestos; 
de esta manera el impuesto calculado es el equivalente al impuesto despues del descuento. 
    Ejemplo: Si la suma de las partidas es 300 y el descuento 100, entonces el 16% de 300 mas 16% de -100 
    es lo equivalente al 16% de 200.

    """,
    'category' : 'Accounting & Finance',
    'website': 'http://bias.com.mx/',
    'images' : [],
    'author': 'OpenBIAS',
    'depends' : ['account', 'base','direccion_mx'],
    'data': [
        'security/cfd_mx_groups.xml',
        'security/ir.model.access.csv',
        'data/l10n_mx_states.xml',
        'data/cfd_mx.formapago.csv',

        'views/account_invoice_workflow.xml',

        'views/res_company_view.xml',
        'views/certificate_view.xml',
        'views/invoice_view.xml',
        'views/partner_view.xml',
        'views/invoice_report.xml',
        'views/report_invoice_mx.xml',
        'views/account_journal_view.xml',
        'views/aprobacion_view.xml',
        # 'wizard/reporte_mensual_wizard_view.xml',
        'views/account_view.xml',
        
        'views/res_country_view.xml',
        'data/mail.template.csv',


    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': '_auto_install_l10n',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
