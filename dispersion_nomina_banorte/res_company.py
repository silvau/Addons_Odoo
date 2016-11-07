# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

class res_company(osv.osv):
    _inherit = 'res.company'

    def _check_emisora(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:

            try:
                int(data.emisora)
                if (len(data.emisora) < 5): # Se asegura que se proporcione un numero de 5 digitos
                    return False
            except ValueError:
                return False
        return True
    def _check_cod_serv(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:

            try:
                int(data.cod_serv)
                if (len(data.cod_serv) < 5): # Se asegura que se proporcione un numero de 5 digitos
                    return False
            except ValueError:
                return False
        return True


    _columns = {
        'emisora': fields.char(string='Emisora',size=5),
        'cod_serv': fields.char(string=u'Código de Servicio',size=5),
    }
    _constraints = [(_check_emisora, u'Emisora debe ser numero de 5 Dígitos', ['emisora'])]
    _constraints = [(_check_cod_serv, u'Código de servicio debe ser numero de 5 Dígitos', ['cod_serv'])]

