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

{
    "name" : "Filters by shop",
    "version" : "1.0",
    "author" : "silvau",
    "category" : "Account",
    "description" : """Creates a many2many relationship between users and sale shops then limmits invoice and sale orders to those related.
    """,
    "website" : "http://www.zeval.com.mx/",
    "license" : "AGPL-3",
    "depends" : ["account","sale"],
     'init_xml': [
        'security/filter_by_shop_groups.xml',
        'security/ir.rule.csv'
    ],
    "demo_xml" : [],
    "update_xml" : [     
        "res_users_view.xml", 
        "sale_order_view_tree.xml", 
        "account_invoice_view.xml", 
        "account_invoice_view_tree.xml", 
    ],
    "installable" : True,
    "active" : False,
}
