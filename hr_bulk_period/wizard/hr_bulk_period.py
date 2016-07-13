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

from openerp.osv import fields, osv
class hr_payslip_bulk_period(osv.osv_memory):

    _name ='hr.payslip.bulk.period'
    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'hr_employee_bulk_rel', 'payslip_id', 'employee_id', 'Employees'),
        'period_id': fields.many2one('account.period', 'Period'),
        'all_employees': fields.boolean('All Employees'),
    }
    _defaults = {

        'all_employees': True,

    }
    
    def update_period(self, cr, uid, ids, context=None):
        run_pool = self.pool.get('hr.payslip.run')
        payslip_pool = self.pool.get('hr.payslip')
        payslip_run=run_pool.browse(cr,uid,context.get('active_id',False))
        data = self.read(cr, uid, ids, context=context)[0]
        if not data['all_employees']:
            slip_ids=payslip_pool.search(cr,uid,[('payslip_run_id','=',context.get('active_id',False)),('employee_id','in',data['employee_ids'])])
        else:
            slip_ids=payslip_pool.search(cr,uid,[('payslip_run_id','=',context.get('active_id',False))])
            
        for slip in slip_ids:
            payslip_pool.write(cr,uid, slip, {'period_id': data['period_id'][0]})
        return {'type': 'ir.actions.act_window_close'}

hr_payslip_bulk_period()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
