# -*- coding: utf-8 -*-
import pdb
import time
from openerp.report import report_sxw
from openerp import pooler

class account_voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_voucher, self).__init__(cr, uid, name, context=context)
        self.total = 0.0
        self.total_invoice = 0.0
        self.total_users ={} 
        self.total_users_invoice ={} 
        self.localcontext.update({
                                  'time': time,
                                  'getLines': self._lines_get,
                                  'getPayments': self._payment_details,
                                  'getInvoices': self._invoices,
                                  'getTotal': self._get_total,
                                  'getTotalInvoice': self._get_total_invoice,
                                  'getTotalByUser': self._get_total_users,
                                  'getTotalInvoiceByUser': self._get_total_users_invoice,
                                  })
        self.context = context
    
    def _lines_get(self, voucher):
        voucherline_obj = pooler.get_pool(self.cr.dbname).get('account.voucher.line')
        voucherlines = voucherline_obj.search(self.cr, self.uid,[('voucher_id','=',voucher.id),('amount','!=','0')])
        voucherlines = voucherline_obj.browse(self.cr, self.uid, voucherlines)
        return voucherlines
    
    def _get_all_users(self):
        user_obj = self.pool.get('res.users')
        return user_obj.search(self.cr, self.uid, [])


    def _payment_details(self, form):
        voucher_obj = self.pool.get('account.voucher')
        user_obj = self.pool.get('res.users')
        data = []
        result = {}
        user_ids = form['user_ids'] or self._get_all_users()
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        voucher_ids = voucher_obj.search(self.cr, self.uid, [
                                              ('create_date','>=',form['date_start'] + ' 00:00:00'),
                                              ('create_date','<=',form['date_end'] + ' 23:59:59'),
                                              ('state','=','posted'),
                                              ('type','=','receipt'),
                                              ('company_id','=',company_id)
                                        ])
        for voucher in voucher_obj.browse(self.cr, self.uid, voucher_ids):
            user=voucher.perm_read()[0]['create_uid'][0] 
            if user in user_ids:
                result = {
                    'number': voucher.number,
                    'amount': voucher.amount, 
                    'user': voucher.perm_read()[0]['create_uid'][1], 
                    'client': voucher.partner_id.name, 
                }
                data.append(result)
                self.total += result['amount']
                if result['user'] in self.total_users:
                    user_total=self.total_users[result['user']]
                else:
                    user_total=0.0
                user_total+=result['amount']
                self.total_users.update({result['user']:user_total})
        if data:
            return data
        else:
            return {}
 
    def _get_total(self):
        return self.total
 
    def _get_total_invoice(self):
        return self.total_invoice
    
    def _get_total_users(self):
        totales=[]
        if self.total_users:
            for key,value in self.total_users.items():
                totales.append({
                   'user': key,
                   'total': value,
                })
            return totales
        else:
            return {}
    def _get_total_users_invoice(self):
        totales=[]
        if self.total_users_invoice:
            for key,value in self.total_users_invoice.items():
                totales.append({
                   'user': key,
                   'total': value,
                })
            return totales
        else:
            return {}
 

    def _invoices(self, form):
        invoice_obj = self.pool.get('account.invoice')
        user_obj = self.pool.get('res.users')
        data = []
        result = {}
        user_ids = form['user_ids'] or self._get_all_users()
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        invoice_ids = invoice_obj.search(self.cr, self.uid, [
                                              ('date_invoice','>=',form['date_start'] + ' 00:00:00'),
                                              ('date_invoice','<=',form['date_end'] + ' 23:59:59'),
                                              ('state','=','open'),
                                              ('company_id','=',company_id)
                                        ])
        for invoice in invoice_obj.browse(self.cr, self.uid, invoice_ids):
            user=invoice.perm_read()[0]['create_uid'][0] 
            if user in user_ids:
                result = {
                    'number': invoice.number,
                    'origin': invoice.origin,
                    'amount': invoice.amount_total, 
                    'user': invoice.perm_read()[0]['create_uid'][1], 
                    'client': invoice.partner_id.name, 
                }
                data.append(result)
                self.total_invoice += result['amount']
                if result['user'] in self.total_users_invoice:
                    user_total=self.total_users_invoice[result['user']]
                else:
                    user_total=0.0
                user_total+=result['amount']
                self.total_users_invoice.update({result['user']:user_total})
        if data:
            return data
        else:
            return {}


report_sxw.report_sxw('report.invoice_client_payments', 'account.voucher',
                      'addons/invoice_client_payments_report/reports/invoice_client_payments_report.rml',
                      parser=account_voucher)
        
        
        
        
