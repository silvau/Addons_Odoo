#-*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import tools
from operator import itemgetter
def get_qty_warehouse(obj, cr, uid, ids, fields, args, context=None):
    res = {}
    w_obj =obj.pool.get("stock.warehouse")
    w_ids = [int(x.split("_")[-1]) for x in fields]
    print w_ids
    loc_ids = [w_obj.browse(cr, uid, w_id).lot_stock_id.id for w_id in w_ids]
    if context is None: context = {}
    partial_q = \
    """ COALESCE((select sum(product_qty) from stock_move where
          state = 'done' and
          location_dest_id = %s and
          product_id = %s), 0) -
        COALESCE((select sum(product_qty) from stock_move where
          state = 'done' and 
          location_id = %s and
          product_id = %s), 0) as loc_%s
    """
    for rec in obj.browse(cr, uid, ids):
        res[rec.id] = {}
        cr.execute("select %s"%(','.join(
          [partial_q%(loc_id, rec.id, loc_id, rec.id, loc_id) for loc_id in loc_ids]
        )))
        for n,col in enumerate(cr.fetchone()):
            res[rec.id]["qty_warehouse_%s"%w_ids[n]] = col
    return res
    
class reporte_almacenes(osv.Model):
    _name = "reporte_almacenes.reporte"
    _auto = False
    
    _columns = {
        'name': fields.many2one("product.product", string="Producto"),
        'default_code': fields.related("name", "default_code", type="char", string="Referencia"),
        'list_price': fields.related("name", "list_price", type="float", string="Precio Lista"),
        'standard_price': fields.related("name", "standard_price", type="float", string="Costo"),
        
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'reporte_almacenes_reporte')
        cr.execute("create or replace view reporte_almacenes_reporte as ("+\
                "select id, id as name from product_product)")
    
    def __init__(self, pool, cr):
        cr.execute("select id,name from stock_warehouse")
        model_obj = pool.get("ir.model.data")
        view_obj = pool.get("ir.ui.view")
        tree_arch = '<tree string="Productos por almacen">\n'
        tree_arch += '<field name="name"/>\n'
        tree_arch += '<field name="default_code"/>\n'
        tree_arch += '<field name="list_price"/>\n'
        tree_arch += '<field name="standard_price"/>\n'
        unsorted_warehouse=[]
        for row in cr.fetchall():
            field_name = "qty_warehouse_%s"%row[0]
            self._columns[field_name] = fields.function(get_qty_warehouse, type="float", method=False, string=row[1], multi="qtys")
            unsorted_warehouse.append(['<field name="%s"/>\n'%field_name,row[1]])
        
        sorted_warehouse=sorted(unsorted_warehouse,key=itemgetter(1))
        ordered_fields=""
        for item in sorted_warehouse:
            ordered_fields+=item[0]
        tree_arch += ordered_fields+'</tree>'
        res = super(reporte_almacenes, self).__init__(pool, cr)
        try:
            view_rec = model_obj.get_object_reference(cr, 1, 'reporte_almacenes', 'reporte_view_tree')
            view_id_tree = view_rec and view_rec[1] or False
            if view_id_tree:
                view_obj.write(cr, 1, view_id_tree, {'arch': tree_arch})
        except ValueError:
            pass
        return res    
