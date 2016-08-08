# -*- encoding: utf-8 -*-
{
    'name': 'Group RH account moves',
    'description': """
    """,
    'version': '1.1.0',
    'author': "silvau",
    'license': 'AGPL-3',
    'category': 'Finance',
    'website': 'http://www.zeval.com.mx',
    'depends': ['account',
                'hr_payroll',
                'hr_payroll_account',
               ],
    'data': [
             'views/account_move_form.xml',
             ],
    'active': False,
    'installable': True,
    'application': True,
}
