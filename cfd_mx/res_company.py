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




from openerp.osv import osv, fields

class company(osv.Model):

    _inherit = 'res.company'
    
    _columns = {
        "cfd_mx_version": fields.selection([('2.2','CFD 2.2'), ('3.2', 'CFDI 3.2')], 'Versión', required=True),
        "cfd_mx_test": fields.boolean('Timbrar en modo de prueba'),
        "cfd_mx_test_nomina": fields.boolean(u'Timbrar en modo de prueba (nómina)'),
        'cfd_mx_pac': fields.selection([('zenpar', 'Zenpar (EDICOM)'), ('tralix','Tralix'), ('finkok', 'Finkok')], string="PAC"),
        "cfd_mx_tralix_key": fields.char("Tralix Customer Key", size=64),
        "cfd_mx_tralix_host": fields.char("Tralix Host", size=256),
        "cfd_mx_tralix_host_test": fields.char("Tralix Host Modo Pruebas", size=256),
        "cfd_mx_finkok_user": fields.char("Finkok user", size=64),
        "cfd_mx_finkok_key": fields.char("Finkok password", size=64),
        "cfd_mx_finkok_host": fields.char("Finkok URL Stamp", size=256),
        "cfd_mx_finkok_host_cancel": fields.char("Finkok URL Cancel", size=256),
        "cfd_mx_finkok_host_test": fields.char("Finkok URL Stamp Modo Pruebas", size=256),
        "cfd_mx_finkok_host_cancel_test": fields.char("Finkok URL Cancel Modo Pruebas", size=256),
        "cfd_mx_journal_ids": fields.many2many("account.journal", string="Diarios"),
    }
    
    _defaults = {
        'cfd_mx_version': '3.2',
        'cfd_mx_test': True,
        'cfd_mx_pac': 'zenpar',
    }
    
company()
