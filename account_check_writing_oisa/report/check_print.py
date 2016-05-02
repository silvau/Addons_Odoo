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
import time
from openerp.report import report_sxw
from openerp.tools import amount_to_text_en
import pdb
class report_print_check_oisa(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_print_check_oisa, self).__init__(cr, uid, name, context)
        self.number_lines = 0
        self.number_add = 0
        self.localcontext.update({
            'time': time,
            'get_lines': self.get_lines,
            'get_moves': self.get_moves,
            'get_sum_debits': self.get_sum_debits,
            'get_sum_credits': self.get_sum_credits,
            'get_mydate': self.get_mydate,
            'fill_stars' : self.fill_stars,
        })

    def get_mydate(self,mydate):
        lista=mydate.split('-',2)
        anio=lista[0] or ''
        mes=lista[1] or ''
        if mes=="01":
           mes="Enero"
        elif mes=="02":
           mes="Febero"
        elif mes=="03":
           mes="Marzo"
        elif mes=="04":
           mes="Abril"
        elif mes=="05":
           mes="Mayo"
        elif mes=="06":
           mes="Junio"
        elif mes=="07":
           mes="Julio"
        elif mes=="08":
           mes="Agosto"
        elif mes=="09":
           mes="Septiembre"
        elif mes=="10":
           mes="Octubre"
        elif mes=="11":
           mes="Noviembre"
        elif mes=="12":
           mes="Diciembre"
        else:
           mes="ERROR"
        dia=lista[2] or ''
        return dia+' de '+mes+' del '+anio

    def fill_stars(self, amount):
        if len(amount) < 100:
            stars = 100 - len(amount)
            return ' '.join([amount,'*'*stars])

        else: return amount
    
    def get_lines(self, voucher_lines):
        result = []
        self.number_lines = len(voucher_lines)
        for i in range(0, min(10,self.number_lines)):
            if i < self.number_lines:
                res = {
                    'date_due' : voucher_lines[i].date_due,
                    'name' : voucher_lines[i].name,
                    'amount_original' : voucher_lines[i].amount_original and voucher_lines[i].amount_original or False,
                    'amount_unreconciled' : voucher_lines[i].amount_unreconciled and voucher_lines[i].amount_unreconciled or False,
                    'amount' : voucher_lines[i].amount and voucher_lines[i].amount or False,
                }
            else :
                res = {
                    'date_due' : False,
                    'name' : False,
                    'amount_original' : False,
                    'amount_due' : False,
                    'amount' : False,
                }
            result.append(res)
        return result
    def get_moves(self, voucher_lines):
        result = []
        self.number_lines = len(voucher_lines)
        for i in range(0, min(10,self.number_lines)):
            res = {
                'account_name' : voucher_lines[i].account_id.name,
                'account' : voucher_lines[i].account_id.code,
                'debit' : voucher_lines[i].debit,
                'credit' : voucher_lines[i].credit,
            }
            result.append(res)
        return result
    def get_sum_debits(self, voucher_lines):
        self.number_lines = len(voucher_lines)
        res={'debit': 0,}
        for i in range(0, min(10,self.number_lines)):
            res = {
                'debit' : res['debit']+voucher_lines[i].debit,
            }
        return res
    def get_sum_credits(self, voucher_lines):
        self.number_lines = len(voucher_lines)
        res={'credit': 0,}
        for i in range(0, min(10,self.number_lines)):
            res = {
                'credit' : res['credit']+voucher_lines[i].credit,
            }
        return res


report_sxw.report_sxw(
    'report.account.print.check.top_oisa',
    'account.voucher',
    'addons/account_check_writing_oisa/report/check_print_top.rml',
    parser=report_print_check_oisa,header=False
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
