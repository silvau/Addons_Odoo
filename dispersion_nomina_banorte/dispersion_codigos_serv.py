# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
import pdb

class dispersion_codigos_serv(osv.osv):
    _name = 'dispersion.codigos_serv'
    _description = 'Codigos de servicio'

    _columns = {
        'name' :fields.char(
        string='Codigo de Servicio',
        size=5,
        required=True,
        readonly=False,
        ),
     }


    def _check_unique_constraint(self,cr,uid,ids,context=None):
        #pdb.set_trace()
        sr_ids = self.search(cr, 1 ,[], context=context)
        lst = [
                x.name.lower() for x in self.browse(cr, uid, sr_ids, context=context)
                if x.name and x.id not in ids
              ]
        for self_obj in self.browse(cr, uid, ids, context=context):
            if self_obj.name and self_obj.name.lower() in  lst or (len(self_obj.name) <> len(self_obj.name.strip())) or (len(self_obj.name) <> 5):
                return False
        return True

    _constraints = [(_check_unique_constraint, 'El nombre debe ser único y no debe tener espacios al inicio o final. Debe ser de 5 digitos', ['name'])]
