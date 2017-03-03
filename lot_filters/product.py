# -*- coding: utf-8 -*-

from openerp.osv import fields, osv, orm
import pdb

class product_category(osv.osv):
 
    _inherit = 'product.category'



    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        """Search for records that have a display name matching the given ``name`` pattern if compared
           with the given ``operator``, while also matching the optional search domain (``args``).
           This is used for example to provide suggestions based on a partial value for a relational
           field.
           Sometimes be seen as the inverse function of :meth:`~.name_get`, but it is not
           guaranteed to be.

           This method is equivalent to calling :meth:`~.search` with a search domain based on ``name``
           and then :meth:`~.name_get` on the result of the search.

           :param list args: optional search domain (see :meth:`~.search` for syntax),
                             specifying further restrictions
           :param str operator: domain operator for matching the ``name`` pattern, such as ``'like'``
                                or ``'='``.
           :param int limit: optional max number of records to return
           :rtype: list
           :return: list of pairs ``(id,text_repr)`` for all matching records.
        """
        name=name.split('/')
        name2=name[len(name)-1]
        name2=name2.strip()
        res2 = super(product_category,self).name_search(cr,user,name2,args,operator,context,limit)
        return res2


