class AuthModule:
    _instance = None
    _display_name = 'Local'
    
    @staticmethod
    def instance():
        return AuthModule._instance

    @staticmethod
    def initialize(app, config):
        if not AuthModule._instance:
            AuthModule._instance = AuthModule(app, config)
        return AuthModule._instance
        
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.display_name = AuthModule._display_name
        
    def authenticate(self, **args):
        user = args['user']
        passwd = args['password']

        log = self.app.logger
        if log:
            log.debug('Local authentication: %s', args)
            
        if user.password != passwd:
            log.debug('Wrong password')
            return 1, False
            
        return 1, True
    
    def __repr__(self):
        return 'Ruther Local Authentication Module'