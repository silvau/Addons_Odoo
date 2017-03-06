# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp.tools.translate import _
import pdb
class sale_order(osv.Model):
    _inherit = 'sale.order'


    def action_button_confirm2(self, cr, uid, ids, context=None):
        rec = self.browse(cr, uid, ids[0])
        leyenda ="Hay productos de papel con existencia: \n\n"
        hay_leyenda = False
        for line in rec.order_line:
            if line.product_id.es_caja:
                if line.product_id.qty_available > 0 :
                   hay_leyenda= True
                   leyenda = leyenda + line.product_id.name + " tiene existencia disponible de: " +str(line.product_id.qty_available)+ "\n"
        if hay_leyenda:

                                                                                                            
            return {
                    'name':_("Pedido con Cajas Disponibles"),#Name You want to display on wizard
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'sale.order.wizard',# With . Example sale.order
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                   # 'domain': '[if you need]',
                    'context': {'default_leyenda':leyenda}
                  }


        res=self.action_button_confirm(cr, uid, ids, context=context)
        return res
