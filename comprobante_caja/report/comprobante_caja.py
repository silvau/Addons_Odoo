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
import pdb
import time
from datetime import datetime
from pytz import timezone
from openerp import pooler
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _

class comprobante_caja_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(comprobante_caja_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_my_date': self.get_my_date, 
    
        })
    
    def get_my_date(self,tz):
        fmt = "%d-%m-%Y %X"
        
        # Get current time
        now_utc = datetime.now(timezone('UTC'))
         
        # Convert to user time zone
        if tz:
            adjusted_date=now_utc.astimezone(timezone(tz))
        else:
            adjusted_date=now_utc
        return adjusted_date.strftime(fmt)   

report_sxw.report_sxw('report.comprobante.caja','pos.session','addons/comprobante_caja/report/comprobante_caja.rml',parser=comprobante_caja_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
