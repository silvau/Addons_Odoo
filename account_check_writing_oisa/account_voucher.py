# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv,fields
from openerp.tools.translate import _
from numero_letras import numero_a_letras
from lxml import etree
import decimal
import pdb

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    def _amount_to_text(self, cr, uid, amount, currency_id, context=None):
        # Currency complete name is not available in res.currency model
        # Exceptions done here (EUR, USD, BRL) cover 75% of cases
        # For other currencies, display the currency code
        currency = self.pool['res.currency'].browse(cr, uid, currency_id, context=context)
        if currency.name.upper() == 'EUR':
            currency_name = 'Euro'
        elif currency.name.upper() == 'USD':
            currency_name = 'Dollars'
        elif currency.name.upper() == 'BRL':
            currency_name = 'reais'
        else:
            currency_name = currency.name
        #TODO : generic amount_to_text is not ready yet, otherwise language (and country) and currency can be passed
        #amount_in_word = amount_to_text(amount, context=context)
        cantidad_entera=int(amount)
        cantidad_decimal=int(100*round(amount%1,2))
        if cantidad_decimal<10:
           cantidad_decimal="0"+str(cantidad_decimal)
        else:
           cantidad_decimal=str(cantidad_decimal)
        cantidad_letras=numero_a_letras(cantidad_entera).upper()+' PESOS '+cantidad_decimal+'/100 M.N.'
        cantidad_letras=cantidad_letras.replace('MILLON PESOS','MILLON DE PESOS',1)
        cantidad_letras=cantidad_letras.replace('MILLONES PESOS','MILLONES DE PESOS',1)
        cantidad_letras=cantidad_letras.replace('CIENTO MILLONES','CIEN MILLONES',1)
        cantidad_letras=cantidad_letras.replace('CIENTO MIL ','CIEN MIL ',1)
        cantidad_letras=cantidad_letras.replace('CIENTO PESOS','CIEN PESOS',1)
        if cantidad_letras.startswith('UNO PESOS'):
            cantidad_letras=cantidad_letras.replace('UNO PESOS','UN PESO',1)
        else:
            cantidad_letras=cantidad_letras.replace('UNO PESOS','UN PESOS',1)
 
#        pdb.set_trace()
        return cantidad_letras

    def print_check(self, cr, uid, ids, context=None):
        if not ids:
            return  {}

        check_layout_report = {
            'oisa' : 'account.print.check.top_oisa',
            'top' : 'account.print.check.top',
            'middle' : 'account.print.check.middle',
            'bottom' : 'account.print.check.bottom',
        }

        check_layout = self.browse(cr, uid, ids[0], context=context).company_id.check_layout
        return {
            'type': 'ir.actions.report.xml', 
            'report_name':check_layout_report[check_layout],
            'datas': {
                    'model':'account.voucher',
                    'id': ids and ids[0] or False,
                    'ids': ids and ids or [],
                    'report_type': 'pdf'
                },
            'nodestroy': True
            }
account_voucher()
