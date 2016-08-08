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

from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
# Entries
#----------------------------------------------------------
class account_move(osv.osv):
    _inherit = "account.move"

    _columns = {
        'nomina_id': fields.many2one('hr.payslip.run', 'Nomina'),
        'slip_id': fields.many2one('hr.payslip', 'Slip'),
        'slip_total': fields.related('slip_id','total',string='Total Slip', readonly=True),
    }

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        res = super(account_move, self).read_group(cr, uid, domain, fields, groupby, offset, limit=limit, context=context, orderby=orderby)
        if 'slip_total' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(cr, uid, line['__domain'], context=context)
                    slip_total_value = 0.0
                    for current_account in self.browse(cr, uid, lines, context=context):
                        slip_total_value += current_account.slip_total
                    line['slip_total'] = slip_total_value
        return res



