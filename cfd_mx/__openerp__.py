# -*- encoding: utf-8 -*-
############################################################################
#    Module for OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Zenpar - http://www.zeval.com.mx/
#    All Rights Reserved.
############################################################################
#    Coded by: jsolorzano@zeval.com.mx
#    Manager: Orlando Zentella ozentella@zeval.com.mx
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################



 
{
    'name' : 'Factura Electronica Mexico',
    'version' : '1.0',
    'author' : 'Zenpar',
    'website' : 'http://www.zeval.com.mx',
    'category' : 'Invoicing',
    'depends' : ['account', 'sale', 'direccion_mx', 'document'],
    'description': """
Modulo para generar los xml de la factura electronica

Nota acerca de los descuentos: para hacer un cfdi con descuento, hay que poner una partida extra
con la cantidad negativa. Ejemplo: para poner un descuento de $100, poner una partida cuyo precio sea
-100. Importante que esta partida tenga impuestos. De esta manera el impuesto calculado es el
equivalente al impuesto después del descuento. Ejemplo: si la suma de las partidas es 300 y 
el descuento 100, entonces el 16% de 300 más 16% de -100 es lo equivalente al 16% de 200.
    """,
    'init_xml': [
        'security/cfd_mx_groups.xml',
        'security/ir.model.access.csv',
        'data/cfd_mx.formapago.csv'
    ],
    'data': [
        'res_company_view.xml',
        'certificate_view.xml',
        'wizard/subir_xml_view.xml',
        'invoice_view.xml',
        'partner_view.xml',
        'account_journal_view.xml',
        'aprobacion_view.xml',
        'wizard/reporte_mensual_wizard_view.xml',
        'account_view.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
