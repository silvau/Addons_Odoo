# -*- encoding: utf-8 -*-
############################################################################
#    Module for OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Zenpar - http://www.zeval.com.mx/
#    All Rights Reserved.
############################################################################
#    Coded by: jsolorzano@zeval.com.mx
#    Manager: Orlando Zentella ozentella@zeval.com.mx
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
    'name' : 'Bulk period on payslip',
    'version' : '1.0',
    'author' : 'silvau',
    'website' : 'http://www.zeval.com.mx',
    'category' : 'HR',
    'depends' : ['hr_payroll'],
    'data': [
        'wizard/hr_bulk_period.xml',
        'hr_payroll_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
