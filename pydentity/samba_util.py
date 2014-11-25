from samba.dcerpc import lsa, samr, security

SECURITY_FLAG = security.SEC_FLAG_MAXIMUM_ALLOWED
CONNECTIONS = {}

def get_connection_obj(conf_file):
    """
    Get the SAMR connection for the given conf file, via ncalrpc. Reuse cache
    where possible.
    """
    if conf_file not in CONNECTIONS:
        CONNECTIONS[conf_file] = samr.samr('ncalrpc:', conf_file)

    return CONNECTIONS[conf_file]

class SAMRHandle(object):
    """
    Wrapper around low level Samba/SAMR API operations
    """
    _handle_obj = None

    def __init__(self, connection_obj=None, conf_file=None):
        assert filter(bool, (connection_obj, conf_file)), \
               "One of connection_obj, or conf_file is provided"

        if connection_obj:
            self._connection_obj = connection_obj
        elif conf_file:
            self._connection_obj = get_connection_obj(conf_file)

    @property
    def handle_obj(self):
        """
        Samba policy_handle connection object
        """
        if not self._handle_obj:
            self._handle_obj = self.connection_obj.Connect(
                0, SECURITY_FLAG
            )

        return self._handle_obj

    @property
    def connection_obj(self):
        """
        Samba samr object
        """
        return self._connection_obj

    def get_domain_sid_obj(self, domainname):
        """
        Get a Samba dom_sid object for the given domain name
        """
        domainname_lsa = lsa.String()
        domainname_lsa.string = unicode(domainname)
        return self.connection_obj.LookupDomain(
            self.handle_obj, domainname_lsa,
        )

    def get_domain_obj(self, sid_obj):
        """
        Get a Samba policy_handle domain object for the given dom_sid object
        """
        return self.connection_obj.OpenDomain(
            self.handle_obj, SECURITY_FLAG, sid_obj
        )

    def get_domain_users_obj(self, domain_obj):
        """
        Get a SamArray object, contaning users for the given policy_handle
        domain object
        """
        # EnumDomainUsers returns (resume handle, users obj, count)
        return self.connection_obj.EnumDomainUsers(domain_obj, 0, 0, -1)[1]

    def get_domain_groups_obj(self, domain_obj):
        """
        Get a SamArray object, contaning groups for the given policy_handle
        domain object
        """
        # EnumDomainGroups returns (resume handle, groups obj, count)
        return self.connection_obj.EnumDomainGroups(domain_obj, 0, -1)[1]
