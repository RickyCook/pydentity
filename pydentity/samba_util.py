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

def enum_iter_for(enum_func, resume_handle):
    """
    Single yield for the SamEntry retuned by resume_handle
    """
    resume_handle, array_obj, _ = enum_func(resume_handle)
    return resume_handle, array_obj.entries[0]

def enum_iter(enum_func, resume_handle=-1):
    """
    Iterator for EnumDomainX calls
    """
    while resume_handle:
        # From the beginning
        if resume_handle == -1:
            resume_handle = 0

        resume_handle, entry_obj = enum_iter_for(enum_func, resume_handle)
        yield entry_obj

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
    def policy_handle_obj(self):
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
            self.policy_handle_obj, domainname_lsa,
        )

    def get_domain_users_obj(self, domain_obj):
        """
        Get a SamArray object, contaning users for the given policy_handle
        domain object
        """
        # EnumDomainUsers returns (resume handle, users obj, count)
        return self.connection_obj.EnumDomainUsers(domain_obj, 0, 0, -1)[1]

    def get_domain_users_obj_iter(self, domain_obj, resume_handle=-1):
        """
        Iterator to load SamEntry user objects one by one
        """
        return enum_iter(lambda rh: self.connection_obj.EnumDomainUsers(
            domain_obj, rh, 0, 1
        ), resume_handle)

    def get_domain_groups_obj(self, domain_obj):
        """
        Get a SamArray object, contaning groups for the given policy_handle
        domain object
        """
        # EnumDomainGroups returns (resume handle, groups obj, count)
        return self.connection_obj.EnumDomainGroups(domain_obj, 0, -1)[1]

    def get_domain_groups_obj_iter(self, domain_obj, resume_handle=-1):
        """
        Iterator to load SamEntry group objects one by one
        """
        return enum_iter(lambda rh: self.connection_obj.EnumDomainGroups(
            domain_obj, rh, 1
        ), resume_handle)

    def get_domain_aliases_obj(self, domain_obj):
        """
        Get a SamArray object, contaning aliases for the given policy_handle
        domain object
        """
        # EnumDomainAliases returns (resume handle, groups obj, count)
        return self.connection_obj.EnumDomainAliases(domain_obj, 0, -1)[1]

    def get_domain_aliases_obj_iter(self, domain_obj, resume_handle=-1):
        """
        Iterator to load SamEntry alias objects one by one
        """
        return enum_iter(lambda rh: self.connection_obj.EnumDomainAliases(
            domain_obj, rh, 1
        ), resume_handle)
