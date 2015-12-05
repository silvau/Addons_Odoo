{
   'name': 'Invoice Client Payments',
   'version': '0.01',
   'category': 'Extra Reports for POS',
   'description': """
   The extra POS reports,
 
   * Reports
     - Report of Invoice Client Payments
 
   """,
   'author': 'silvau',
   'website': 'http://www.zenpar.com.mx',
   'depends': ['account','point_of_sale'],
   'data': [
       'wizard/invoice_client_payments_wizard_view.xml',
       'reports.xml',
   ],
   'installable': True,
   'active': False,
}
