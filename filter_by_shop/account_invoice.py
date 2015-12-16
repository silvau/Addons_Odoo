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
class account_invoice(osv.osv):
    _inherit = 'account.invoice'
  

    def _get_default_shop(self, cr, uid, context=None):
        shops = self.pool.get('res.users').browse(cr, uid, uid, context=context).shops
        shop_ids = self.pool.get('sale.shop').search(cr, uid, [('id','in',tuple(g.id for g in shops))], context=context)
        if not shop_ids:
            return 0
        return shop_ids[0]

   
    
    _columns = {
        'shop_id': fields.many2one('sale.shop', string='Shop', required=True),
    }


    _defaults = {
 
        'shop_id': _get_default_shop, 
   }

