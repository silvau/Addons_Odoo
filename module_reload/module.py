from openerp.modules.registry import RegistryManager
from openerp.netsvc import Service
from osv import fields, osv
from osv.orm import MetaModel

from reimport import reimport

class module(osv.osv):
    _inherit = "ir.module.module"

    def button_reload(self, cr, uid, ids, context=None):
        for module_record in self.browse(cr, uid, ids, context=context):
            #Remove any report parsers registered for this module.
            module_path = 'addons/' + module_record.name
            for service_name, service in Service._services.items():
                template = getattr(service, 'tmpl', '')
                if type(template) == type(''):
                    if template.startswith(module_path):
                        Service.remove(service_name)
            
            #Remove any model classes registered for this module
            MetaModel.module_to_models[module_record.name] = []                    
            
            #Reload all Python modules from the OpenERP module's directory.
            modulename = 'openerp.addons.' + module_record.name
            root = __import__(modulename)
            module = getattr(root.addons, module_record.name)
            
            reimport(module)
        RegistryManager.delete(cr.dbname)
        RegistryManager.new(cr.dbname)
        return {}
        
module()
