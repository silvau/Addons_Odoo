{
   'name': 'Dispersion Nomina Banorte',
   'version': '0.01',
   'category': 'Extra Reports for HR',
   'description': """
   Creates a text file to send the payslip through the Banorte Bank 
   """,
   'author': 'silvau',
   'website': 'http://www.zenpar.com.mx',
   'depends': ['hr','cfdi_nomina'],
   'init_xml': [
        'security/ir.model.access.csv',
    ],

   'data': [
       'wizard/hr_payslip_dispersion_wizard_view.xml',
#       'res_company_view.xml',
       'hr_employee_view.xml',
       'dispersion_emisoras_view.xml',
       'dispersion_codigos_serv_view.xml',
#       'reports.xml',
   ],
   'installable': True,
   'active': False,
}
