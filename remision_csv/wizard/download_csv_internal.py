# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields
import base64
import re

class wizard_generar_xmls(osv.TransientModel):
    _name = 'download.csv.internal'


    def _create_csv(self, cr, uid, id, data, header):
        rows = []
        for record in data['partidas']:
            row = [data['num_remision'],data['proveedor'],data['oc']]
            for col in header:
                row.append(record.get(col, ' '))
            rows.append(row)
        header.insert(0,'oc')
        header.insert(0,'proveedor')
        header.insert(0,'num_remision')
        csv = ",".join([str(x) for x in header]) + "\n"
        for row in rows:
            csv += ",".join([str(x) for x in row]) + "\n"
        csv_base64 = base64.encodestring(csv.encode("utf-8")) or ''
        return csv_base64


    def _export_to_csv(self, cr, uid, ids, context=None):
        stock_picking_obj=self.pool.get('stock.picking')
        this = stock_picking_obj.browse(cr, uid, ids[0])
        data = {
            'num_remision': this.name ,
            'proveedor': this.partner_id.name ,
            'oc': this.purchase_id.name,
            'partidas': []
            }
        stock_move_obj = self.pool.get("stock.move")
        
        move_ids=[]
        for i in this.move_lines:
            move_ids.append(i.id)

        for move in stock_move_obj.browse(cr, uid, move_ids):
            partida = {
                'codigo': move.product_id.default_code,
                'cantidad': move.product_qty,
                'uom': move.product_uom.name,
                'lote': move.prodlot_id.name,
                }
            data['partidas'].append(partida)
        csv_header = ["codigo", "cantidad", "uom", "lote"]
        res = self._create_csv(cr, uid, this.id, data, csv_header)
        return res

    def _get_fname_csv(self, cr, uid,context):
        stock_picking_obj=self.pool.get('stock.picking')
        this = stock_picking_obj.browse(cr, uid, context['active_id'])
        fname = re.sub(r'(?u)[^-\w.]','',this.name.strip().replace(' ','_')) +".csv"
        return fname

    def _get_file(self,cr,uid,context):
        res=self._export_to_csv(cr, uid,context['active_ids'])
        return res
    

    _columns = {
        'csv' : fields.binary (string='File'),
        'fname_csv': fields.char("Filename CSV"),
    }
    _defaults = {
       
        'fname_csv': _get_fname_csv,
        'csv': _get_file,
    }



