import oerplib
env = oerplib.OERP('localhost', protocol='xmlrpc', port=8089)
user = env.login('admin', 'admin', 'db_name')
currency_obj = env.get('res.currency')
currency_obj.run_currency_update()