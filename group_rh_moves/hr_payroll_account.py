#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp import netsvc
from datetime import date, datetime, timedelta

from openerp.osv import fields, osv
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _
#import pdb
class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'

    def process_sheet(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        res = super(hr_payslip, self).process_sheet(cr, uid, ids, context=context)
        #pdb.set_trace()
        move_id=self.browse(cr,uid,ids)[0].move_id.id
        total_slip=self.browse(cr,uid,ids)[0].total
        nomina_id=self.browse(cr,uid,ids)[0].payslip_run_id.id
        move_pool.write(cr, uid, [move_id], {'nomina_id': nomina_id,'slip_id':ids[0],'total_slip':total_slip}, context=context)

        return res
hr_payslip()
