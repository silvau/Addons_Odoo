import pdb
from openerp.osv import osv, fields
from openerp.tools.translate import _



class sale_order_wizard(osv.osv_memory):
    _name = 'sale.order.wizard'
    
    _columns = {
             'leyenda': fields.text('Leyenda', readonly= True)
              }
    def ajustar(self,cr,uid,ids,context=None):
        obj_sale_order=self.pool.get('sale.order')
        res=obj_sale_order.action_button_confirm(cr, uid, context['active_ids'], context=context)
        return res

    def no_ajustar(self,cr,uid,ids,context=None):
         
        return {'type': 'ir.actions.act_window_close'} 

    

