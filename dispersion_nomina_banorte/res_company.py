# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Zenpar - http://www.zeval.com.mx/
#    All Rights Reserved.
############################################################################
#    Coded by: jsolorzano@zeval.com.mx
#    Launchpad Project Manager for Publication: Orlando Zentella ozentella@zeval.com.mx
############################################################################
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

