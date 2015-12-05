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
from openerp import pooler
from netsvc import Service

class picking_palmas(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking_palmas, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_name': self.get_name,
            'get_product_desc': self.get_product_desc,
        })
    def get_product_desc(self, move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc

    def get_name(self,obj):
        self.cr.execute("""

                       SELECT create_uid,write_uid from stock_move where id = %s 

                       """ %(obj.id))
        res=self.cr.fetchall()
        name=pooler.get_pool(self.cr.dbname).get('res.users').browse(self.cr, self.uid, res[0][0]).name
        return name

# remove previous stock report service :
#del Service._services['report.stock.picking.list']


report_sxw.report_sxw('report.stock.picking.list_palmas','stock.picking','reportes_palmas/reportes/picking.rml',parser=picking_palmas, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
