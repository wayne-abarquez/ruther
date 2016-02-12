import os, imp
from app import app
import config

class AuthModuleFactory:
    mods = {}
    @staticmethod
    def init ( auth_module_directory):
        files = []
        
        for obj in os.listdir(auth_module_directory):
            files.append(obj)
        

        for obj in files:
            filename, ext = '', ''
            try:
                filename, ext = obj.split('.')
            except:
                pass
            
            if filename and ext and os.path.isfile(os.path.join(auth_module_directory, obj)) and filename != '__init__' and ext == 'py':
                _ = imp.load_source(filename,os.path.join(auth_module_directory, obj)) #__import__ (filename)

                _auth_module = _.AuthModule.initialize(app, config)

                AuthModuleFactory.mods[filename] = _auth_module
                # if AuthModule.validateModule(_):
                    # AuthModule.mods[filename] = {'DisplayName' : _.DisplayName, 'Module': _ }

        # end for

    @staticmethod
    def Authenticate(module_name, **args):
        print 'Authenticating using %s' % ( module_name, )
        return AuthModuleFactory.mods[module_name].authenticate(**args)

    @staticmethod
    def validateModule(module):
        if not hasattr(module, 'authenticate'):
            return False

        return True

    @staticmethod
    def list_all_available_modules():
        return mods
        
    @staticmethod
    def getAvailableUsers(module_name, **args):
        return AuthModuleFactory.mods[module_name].getAvailableUsers(**args)
        
    @staticmethod
    def getList(module_name, **args):
        return AuthModuleFactory.mods[module_name].getList(**args)