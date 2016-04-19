# -*- encoding: utf-8 -*-
##############################################################################
#
#    Authors: Nicolas Bessi, Guewen Baconnier
#    Copyright Camptocamp SA 2011
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
    'name': 'Account Report Oisa',
    'description': """
    """,
    'version': '1.1.0',
    'author': "silvau,amptocamp,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Finance',
    'website': 'http://www.zeval.com.mx',
    'depends': ['account',
                'report_webkit'],
    'data': [
             'wizard/partners_ledger_wizard_view.xml',
             'report.xml',
             ],
    'active': False,
    'installable': True,
    'application': True,
}
