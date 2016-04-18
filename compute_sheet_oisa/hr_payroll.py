# -*- encoding: utf-8 -*-
from openerp.osv import osv,fields

class hr_payslip_run(osv.Model):
    _inherit = 'hr.payslip.run'

    def compute_sheet_all(self, cr, uid, ids, context=None):
        
        payslip_obj=self.pool.get('hr.payslip')
        payslip_run_obj=self.pool.get('hr.payslip.run')
        my_slip_ids=payslip_run_obj.read(cr,uid,ids,['slip_ids'])
        for slip in my_slip_ids[0]['slip_ids']: 
            child_slip=payslip_obj.browse(cr,uid,slip)
            child_slip.compute_sheet()       
        return True
       
hr_payslip_run()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
