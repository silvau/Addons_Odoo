# -*- encoding: utf-8 -*-

from openerp.osv import fields,osv
from openerp import netsvc
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import pdb


class mrp_repair(osv.osv):
    _inherit = 'mrp.repair'
    
    _columns = {
        'ref_prov': fields.char('Ref Proveedor')
    }

   
    
    def action_confirm(self, cr, uid, ids, *args):
        pdb.set_trace()
        res = super(mrp_repair, self).action_confirm(cr, uid, ids)
        po_obj = self.pool.get("purchase.order")
        for o in self.browse(cr, uid, ids):
            oc_ids= po_obj.search(cr,uid, [('repair_id','=',o.id)])
            po_obj.write(cr,uid,oc_ids,{'partner_ref': o.ref_prov}, context=None)     
        return res

