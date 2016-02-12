import ldap

class AuthModule:
    _instance = None
    _display_name = 'LDAP'
    
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
        self.base_dn = self.config.ldap['base']
        self.user_ou = self.config.ldap['user_ou']
        self.roles_ou = self.config.ldap['roles_ou']
        self.roles_filter = self.config.ldap['roles_filter']
        self.ldap_server = self.config.ldap['host']
        self.manager_cn = self.config.ldap['manager_cn']
        self.manager_secret = self.config.ldap['manager_secret']
       
        self.display_name = AuthModule._display_name
    
    def getRolesList(self):
        rolelist = []
        try:
            Server = self.ldap_server
            # DN, Secret, un = 'cn=Manager,dc=Navagis,dc=local', 'navagis', 'local'
            DN, Secret = 'cn=' + self.manager_cn + ',' + self.base, self.manager_secret
            Base = self.base_dn
            Scope = ldap.SCOPE_SUBTREE
            Filter = self.roles_filter
            Attrs = ["cn", "member"]

            l = ldap.initialize(Server)
            l.protocol_version = 3
            l.set_option(ldap.OPT_REFERRALS, 0)
            
            l.simple_bind_s(DN, Secret)

            r = l.search(Base, Scope, Filter, Attrs)
            Type,user = l.result(r,60)
            self.app.logger.debug( user )
            for obj in user:
                Name, Attrs = obj
                
                if hasattr(Attrs, 'has_key') and Attrs.has_key('cn'):
                
                    displayName = Attrs['cn'][0]
                    rolelist.append([displayName, Attrs['member']])
            
            return rolelist

        except ldap.INVALID_CREDENTIALS, e:
            log.debug('Invalid credentials')
            return False

        except ldap.LDAPError, e:
            print e
            return False     
            
    def getList(self):
        rolelist = []

        try:
            Server = self.ldap_server
            # DN, Secret, un = 'cn=Manager,dc=Navagis,dc=local', 'navagis', 'local'
            DN, Secret = 'cn=' + self.manager_cn + ',' + self.base_dn, self.manager_secret
            Base = self.base_dn
            Scope = ldap.SCOPE_SUBTREE
            Filter = self.roles_filter
            Attrs = ["cn", "member"]
            
            l = ldap.initialize(Server)
            l.protocol_version = 3
            l.set_option(ldap.OPT_REFERRALS, 0)
            
            l.simple_bind_s(DN, Secret)

            r = l.search(Base, Scope, Filter, Attrs)
            Type,user = l.result(r,60)
            self.app.logger.debug( user )
            for obj in user:
                Name, Attrs = obj
                
                if hasattr(Attrs, 'has_key') and Attrs.has_key('cn'):
                   
                    displayName = Attrs['cn'][0]
                   
                    members = [ ]
                    for obj in Attrs['member']:
                        member = {}
                        for entry in obj.split(','):
                            key, value = entry.split('=')
                            member[key] = value
                        members.append(member)
                    role = {'RoleName' : displayName, 'Members' : members }
                    rolelist.append( role )
            
            return 1, rolelist

        except ldap.INVALID_CREDENTIALS, e:
            log.debug('Invalid credentials')
            return -1, []

        except ldap.LDAPError, e:
            print e
            return -1, []    
    
   
    # yes, it's not done yet.
    def authenticate(self, **args):
        user = args['user']
        passwd = args['password']

        log = self.app.logger


        if log:
            log.debug('LDAP authentication: %s', args)

        try:

            Server = self.config.ldap['host']
            # DN, Secret, un = 'cn=Manager,dc=Navagis,dc=local', 'navagis', 'local'
            _ = [ obj.split('=')[1] for obj in self.base_dn.split(',') ]
            domain = _[0]
            for entry in _[1:]:
                domain += '.' + entry



            
            uid, u_domain = user.username.split('@')
            if domain.lower() != u_domain.lower():

                return -1, False
            DN, Secret =  'uid=' + uid + ',ou=' + self.user_ou + ',' + self.base_dn, passwd #self.config.ldap['user_query_dn'] % {'username': user.username}, passwd            
            l = ldap.initialize(Server)
            l.protocol_version = 3
            l.set_option(ldap.OPT_REFERRALS, 0)
            
            l.simple_bind_s(DN, Secret)

            return 1, True
        except ldap.INVALID_CREDENTIALS, e:
            log.error('Invalid credentials: %s', user.username)
            return -1, False

        except ldap.LDAPError, e:
            log.error('LDAPError: %s', e)
            return -1, False
        
    def __repr__(self):
        return 'Ruther LDAP Authentication Module'
