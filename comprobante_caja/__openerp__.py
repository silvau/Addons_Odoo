{
   'name': 'Comprobante de Caja',
   'version': '0.01',
   'category': 'Extra Reports for POS',
   'description': """
   The extra POS reports,
 
   * Reports
     - Ticket for take out cash 2
 
   """,
   'author': 'silvau',
   'website': 'http://www.zenpar.com.mx',
   'depends': ['account','point_of_sale'],
   'data': [
       'wizard/pos_box.xml',
       'reports.xml',
       'point_of_sale_view.xml',
   ],
   'installable': True,
   'active': False,
}
