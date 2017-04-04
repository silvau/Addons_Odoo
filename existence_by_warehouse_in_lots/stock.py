# -*- coding: utf-8 -*-


from openerp.osv import fields, osv, orm
import logging
import pandas as pd
from lxml import etree
import pdb

_logger= logging.getLogger(__name__)



class stock_move(osv.osv):

    _inherit="stock.move"


    def write(self, cr, uid, ids, vals, context=None):
        res = super(stock_move, self).write(cr, uid, ids, vals, context=context)
        status=vals.get('state','')
        if status == 'cancel' or status == 'done':
            lot_existence_obj=self.pool.get('lot.existence')
            lot_ids = self.pool.get('stock.production.lot').search(cr,uid,[('move_ids','in',ids)])
            for lot_id in lot_ids:
                 lot_existence_ids = lot_existence_obj.search(cr,uid,[('lot_id','=',lot_id)])
                 for lot_existence in lot_existence_obj.browse(cr,uid,lot_existence_ids):
                     if lot_existence.existence == 0.0 :
                         lot_existence.unlink()
        return res

    
class lot_existence(osv.osv):
    _name = "lot.existence"
    _rec_name = "lot_id"


    def _set_existences(self, cr, uid, ids=None, context=None):
        if ids is not None:
            raise NotImplementedError("Ids is just there by convention! Please don't use it.")
        lot_obj = self.pool.get('stock.production.lot')
        warehouse_obj = self.pool.get('stock.warehouse')      
        lot_ids = lot_obj.search(cr,uid,[])
        warehouse_ids = warehouse_obj.search(cr,uid,[])
        lot_existence_ids= self.search(cr,uid,[])
        lot_existence_regs_to_add=[]
        if lot_existence_ids:
            lot_existence_regs_in_table=self.read(cr,uid,lot_existence_ids,['lot_id','warehouse_id'])
            lot_existence_reg_dicts = []
            for lot_existence_reg in lot_existence_regs_in_table:
                lot_existence_reg_dicts.append({'lot_id':lot_existence_reg['lot_id'][0], 'warehouse_id':lot_existence_reg['warehouse_id'][0]})
            df = pd.DataFrame(lot_existence_reg_dicts)
            for warehouse_id in warehouse_ids:
                for lot_id in lot_ids:
                    already_in_table= False
                    already_in_table= df[ (df.lot_id == lot_id) & (df.warehouse_id == warehouse_id) ]
                    if (type(already_in_table) == bool and not already_in_table )or(already_in_table.empty):
                        lot_existence_regs_to_add.append({'lot_id': lot_id, 'warehouse_id': warehouse_id})
            for lot_existence_reg_to_add in lot_existence_regs_to_add:
                _logger.info('Agregando registro faltante a lot_existence con lot_id: %s, warehouse_id: %s. ', lot_existence_reg_to_add['lot_id'], lot_existence_reg_to_add['warehouse_id'])

                new_id=0
                new_id=self.create(cr,uid,lot_existence_reg_to_add)
                new_lot_existence= self.browse(cr,uid,new_id)
                if new_lot_existence.existence == 0.0  and new_id:
                    lot_existence_obj.unlink(cr,uid,new_id)
             
        else:                  
            for warehouse_id in warehouse_ids:
               for lot_id in lot_ids:
                   _logger.info('Agregando registro para inicializar lot_existence con lot_id: %s, warehouse_id: %s. ', lot_id, warehouse_id)
                   self.create(cr,uid,{'lot_id':lot_id, 'warehouse_id': warehouse_id}) 
        _logger.info('Inicializacion Terminada')
        return True

    def _get_existence(self, cr, uid, ids, field_name, arg, context=None):
        res ={}
        
        for lot_existence in self.browse(cr,uid,ids):
            existence=0.0
            existence_location_id = lot_existence.warehouse_id.lot_stock_id
            move_ids = lot_existence.lot_id.move_ids
            if not move_ids :
                res[lot_existence.id]= 0.0
                
                continue
            for move in (move for move in move_ids if ((move.location_dest_id == existence_location_id  or move.location_id == existence_location_id)  and move.state == 'done')):
                if move.location_dest_id == existence_location_id:
                    existence += move.product_qty
                if move.location_id == existence_location_id:
                    existence -= move.product_qty
            res[lot_existence.id]=existence 

        return res 

    def _existence_trigger(self,cr,uid,ids,context=None):
        existence_ids=[]
        lot_obj=self.pool.get('stock.production.lot')
        existence_obj=self.pool.get('lot.existence')
        lot_ids=lot_obj.search(cr,uid,[('move_ids','in',ids)])
        existence_ids=existence_obj.search(cr,uid,[('lot_id','in',lot_ids)])
        return existence_ids
       

    _columns = {
        'lot_id': fields.many2one('stock.production.lot','Lote'),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
        'existence': fields.function(_get_existence,method=True, type='float',string='Existence',store={
                                                  'stock.move':(_existence_trigger,[],10),
                                                  'lot.existence':(lambda self,cr,uid, ids,context=None: ids,[],10),
                                                  },
                                     ),
    }

lot_existence()

class stock_production_lot(osv.osv):
 
    _inherit = 'stock.production.lot'


    def _set_domain(self,cr,uid,context=None):
        domain=[]
        flag = self.pool.get('res.users').has_group(cr, uid, 'existence_by_warehouse_in_lots.lot_existence_group') 
        if flag :
            user=self.pool.get('res.users').browse(cr,uid,uid)
            warehouses=[]
            warehouses=[warehouse.id for warehouse in user.warehouses]
            lot_existence_ids=self.pool.get('lot.existence').search(cr,uid,[('existence','>',0),('warehouse_id','in',warehouses)])
            lots= self.pool.get('lot.existence').read(cr,uid,lot_existence_ids,['lot_id'])
            lot_ids = []
            lot_ids=[lot['lot_id'][0] for lot in lots]
            domain.append(('id','in',lot_ids))
        return domain


    def get_lot_existence_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        lot_existence_obj= self.pool.get('lot.existence')
        warehouse_ids=self.pool.get('stock.warehouse').search(cr,uid,[])       
        for id in ids:
            lot_existence_ids=[]
            for warehouse_id in warehouse_ids:
                already_created_id = 0
                already_created_id=lot_existence_obj.search(cr,uid,[('lot_id','=',id),('warehouse_id','=',warehouse_id)])
                if already_created_id:
                    lot_existence_ids.append(already_created_id[0])
		else:
                    new_id=0
                    new_id=lot_existence_obj.create(cr,uid,{'warehouse_id': warehouse_id, 'lot_id': id})
                    new_lot_existence= lot_existence_obj.browse(cr,uid,new_id)
                    if new_lot_existence.existence == 0.0 :
                        lot_existence_obj.unlink(cr,uid,new_id)
                    elif new_id:
                        lot_existence_ids.append(new_id)
                        
                      
	    res[id] = lot_existence_ids
        return res




    def _allowed_prodlot_ids_search(self, cr, uid, obj, name, args, context=None):
        list_of_ids = []
        user=self.pool.get('res.users').browse(cr,uid,uid)
        warehouses=[]
        warehouses=[warehouse.id for warehouse in user.warehouses]
        lot_existence_ids=self.pool.get('lot.existence').search(cr,uid,[('existence','>',0),('warehouse_id','in',warehouses)])
        lots= self.pool.get('lot.existence').read(cr,uid,lot_existence_ids,['lot_id'])
        lot_ids = []
        lot_ids=[lot['lot_id'][0] for lot in lots]
        list_of_ids = self.pool.get('stock.production.lot').search(cr,uid,[('product_id','=',context['product_id']),('id','in',lot_ids)])
        
        return [('id', 'in', list_of_ids)]

    _columns={
    
            'allowed_prodlot_ids': fields.function(
                                   lambda **x: True,
                                   fnct_search=_allowed_prodlot_ids_search,
                                   type='boolean',
                                   method=True,
                                 ),                               

            'lot_existence_ids': fields.function(get_lot_existence_ids, type='one2many', obj='lot.existence',string="Lot Existences")

     }

stock_production_lot()

