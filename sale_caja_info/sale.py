# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb

class sale_order(osv.osv):
    _inherit = "sale.order"


    def _get_caja_id(self, cr, uid, ids, field_name, arg, context):
        so_line_obj=self.pool.get('sale.order.line')
        product_obj=self.pool.get('product.product')
        product_cajas_ids = product_obj.search(cr,uid,[('es_caja','=',True)])
        res={}
        for i in ids:
            cajas=so_line_obj.search(cr,uid,[('product_id','in',product_cajas_ids), ('order_id','=',i)],count=True)
            if cajas > 0 :
                res[i] = so_line_obj.search(cr,uid,[('product_id','in',product_cajas_ids), ('order_id','=',i)],limit=1)
            else:
                res[i] = False
        return res

    def _get_bom_id(self, cr, uid, ids, field_name, arg, context):
        bom_obj=self.pool.get('mrp.bom')
        res={}
        for i in ids:
             product_id= self.browse(cr,uid,i,context=context).caja_id.product_id.id
             res[i]=bom_obj.search(cr,uid,[('product_id','=',product_id)],limit=1)
        return res

    def _get_medidas_filtradas(self, cr, uid, ids, field_name, arg, context):
        medidas_desc_obj=self.pool.get('oisa.cot.caja.desc')
        medidas_obj=self.pool.get('oisa.cotizacion.medidas')
        res={}
        medidas_abc=medidas_desc_obj.search(cr,uid,[('var','in',['a','b','c'])])
        for i in ids:
            medida_ids= self.browse(cr,uid,i,context=context).medidas_cotizacion_caja_id
            lista_ids= []
            for medida in medida_ids:
                lista_ids.append(medida.id)
            res[i]=medidas_obj.search(cr,uid,[('id','in',lista_ids),('name','in',medidas_abc)])
        return res


    _columns = {
        'caja_id': fields.function(_get_caja_id, type='many2one', obj='sale.order.line', method='True',  string='Caja'),
        'bom_id': fields.function(_get_bom_id, type='many2one', obj='mrp.bom', method='True',  string='Lista Pantones'),
        'pantones_caja_id': fields.related('bom_id','bom_lines',type='one2many', relation='mrp.bom',string='Pantones'),
        'cotizacion_caja_id': fields.related('caja_id','product_id','cot_id',type='many2one', relation='oisa.cotizacion',string='Cotizacion de la Caja'),
        'routing_caja_id': fields.related('caja_id','product_id','routing_id',type='many2one', relation='mrp.routing',string='Proceso Productivo'),
        'medidas_cotizacion_caja_id': fields.related('caja_id','product_id','cot_id','medidas',type='one2many', relation='oisa.cotizacion.medidas',string='Medidas de la Caja'),
        'medidas_filtradas': fields.function(_get_medidas_filtradas,type='one2many', obj='oisa.cotizacion.medidas',string='Medidas (ABC)'),
        'wc_cotizacion_caja': fields.related('caja_id','product_id','cot_id','wc',type='float', relation='oisa.cotizacion',string='WC', digits=(12,5)),
        'wi_cotizacion_caja': fields.related('caja_id','product_id','cot_id','wi',type='float', relation='oisa.cotizacion',string='WI', digits=(12,5)),
        'uc_cotizacion_caja': fields.related('caja_id','product_id','cot_id','uc',type='integer', relation='oisa.cotizacion',string='UC'),
        'ui_cotizacion_caja': fields.related('caja_id','product_id','cot_id','ui',type='integer', relation='oisa.cotizacion',string='UI'),
        'chk_flauta_cotizacion_caja': fields.related('caja_id','product_id','cot_id','chk_flauta',type='boolean', relation='oisa.cotizacion',string='(Lleva flauta?)'),
        'chk_laminado_cotizacion_caja': fields.related('caja_id','product_id','cot_id','chk_laminado',type='boolean', relation='oisa.cotizacion',string='(Lleva Laminado?)'),
        'material_cotizacion_caja_id': fields.related('caja_id','product_id','cot_id','material_id',type='many2one', relation='product.product',string='Material'),
        'procesos_cotizacion_caja_id': fields.related('caja_id','product_id','cot_id','proceso_ids',type='one2many', relation='oisa.cot.proceso.ins',string='Procesos de la Caja'),
        'chk_guias_cotizacion_caja': fields.related('caja_id','product_id','cot_id','chk_guias',type='boolean', relation='oisa.cotizacion',string='Guias'),
        'tipo_tabla_cotizacion_caja': fields.related('caja_id','product_id','cot_id','tipo_tabla',type='selection', relation='oisa.cotizacion',string='Tabla'),
        'ean13_cotizacion_caja': fields.related('caja_id','product_id','ean13',type='char', relation='product.product',string='Código EAN13'),
        'num_corrugado_caja': fields.related('caja_id','product_id','num_corrugado',type='integer', relation='product.product',string='Número de Corrugado'),
        'piezas_corrugado_caja': fields.related('caja_id','product_id','piezas_corrugado',type='integer', relation='product.product',string='Piezas / Corrugado'),
        'version_dibujo': fields.related('caja_id','product_id','version',type='char', relation='product.product',string='Versión del Dibujo'),
        'fecha_autorizacion_dibujo': fields.related('caja_id','product_id','fecha_autorizacion_dibujo',type='date', relation='product.product',string='Fecha de Autorización del Dibujo'),
        'version_especificacion': fields.related('caja_id','product_id','version_especificacion',type='char', relation='product.product',string='Versión de la Especificación'),
        'fecha_especificacion': fields.related('caja_id','product_id','fecha_especificacion',type='date', relation='product.product',string='Fecha de la Especificación'),
        'revisar_version_dibujo': fields.related('caja_id','product_id','made_for','revisar_version_dibujo',type='boolean', relation='res.partner', string='Revisar Version del Dibujo'),
        'revisar_fecha_autorizacion_dibujo': fields.related('caja_id','product_id','made_for','revisar_fecha_autorizacion_dibujo',type='boolean', relation='res.partner', string='Revisar Fecha de Autorizacion del Dibujo'),
        'revisar_version_especificacion': fields.related('caja_id','product_id','made_for','revisar_version_especificacion',type='boolean', relation='res.partner', string='Revisar Version de la Especificacion'),
        'revisar_fecha_especificacion': fields.related('caja_id','product_id','made_for','revisar_fecha_especificacion',type='boolean', relation='res.partner', string ='Revisar Fecha de Especificacion'),

    }
