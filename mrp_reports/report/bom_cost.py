# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw

class bom_cost(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bom_cost, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.mrp_reports.bom.cost','mrp.bom','addons/mrp_reports/report/bom_cost.rml',parser=bom_cost, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
