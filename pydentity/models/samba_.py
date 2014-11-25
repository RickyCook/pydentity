class Domain(object):
    """
    A Samba domain
    """
    _sid_obj = None
    _domain_obj = None

    def __init__(self, name, samr_handle):
        self._name = name
        self._samr_handle = samr_handle

    @property
    def name(self):
        """
        Domain name
        """
        return self._name

    @property
    def samr_handle(self):
        """
        SAMRHandle used to retrieve this Domain
        """
        return self._samr_handle

    @property
    def sid_obj(self):
        """
        Samba dom_sid object
        """
        if not self._sid_obj:
            self._sid_obj = self.samr_handle.get_domain_sid_obj(self.name)

        return self._sid_obj

    @property
    def domain_obj(self):
        """
        Samba policy_handle domain object
        """
        if not self._domain_obj:
            self._domain_obj = self.samr_handle.get_domain_obj(self.sid_obj)

        return self._domain_obj

    def _child_property_helper(self, samba_obj_func, child_class):
        """
        Helper for child list properties
        """
        return [
            child_class(self, user_obj.name.string, user_obj.idx)
            for user_obj in samba_obj_func().entries
        ]

    def _child_iter_property_helper(self, samba_obj_iter, child_class):
        """
        Helper for child iterator properties
        """
        for samba_obj in samba_obj_iter:
            yield child_class(self, samba_obj.name.string, samba_obj.idx)

    @property
    def users(self):
        """
        List of users associated with this domain
        """
        return self._child_property_helper(
            lambda: self.samr_handle.get_domain_users_obj(self.domain_obj),
            User,
        )

    def users_iter(self, rid=-1):
        """
        Iterator for users associated with this domain, starting after the
        given RID
        """
        return self._child_iter_property_helper(
            self.samr_handle.get_domain_users_obj_iter(self.domain_obj, rid),
            User,
        )

    @property
    def groups(self):
        """
        List of groups associated with this domain
        """
        return self._child_property_helper(
            lambda: self.samr_handle.get_domain_groups_obj(self.domain_obj),
            Group,
        )

    def groups_iter(self, rid=-1):
        """
        Iterator for groups associated with this domain, starting after the
        given RID
        """
        return self._child_iter_property_helper(
            self.samr_handle.get_domain_groups_obj_iter(self.domain_obj, rid),
            User,
        )

    @property
    def aliases(self):
        """
        List of aliases associated with this domain
        """
        return self._child_property_helper(
            lambda: self.samr_handle.get_domain_aliases_obj(self.domain_obj),
            Alias,
        )

    def aliases_iter(self, rid=-1):
        """
        Iterator for aliases associated with this domain, starting after the
        given RID
        """
        return self._child_iter_property_helper(
            self.samr_handle.get_domain_aliases_obj_iter(self.domain_obj, rid),
            User,
        )

    def __repr__(self):
        return self.__unicode__()
    def __unicode__(self):
        return u"<%s: %s>" % (self.__class__.__name__, self.name)


class DomainChild(object):
    """
    Base class for domain children
    """
    def __init__(self, domain, name, rid):
        self._domain = domain
        self._name = name
        self._rid = rid

    @property
    def domain(self):
        """
        Domain object this user is associated with
        """
        return self._domain

    @property
    def name(self):
        """
        Username
        """
        return self._name

    @property
    def rid(self):
        """
        Relative identifier
        """
        return self._rid

    def __repr__(self):
        return self.__unicode__()
    def __unicode__(self):
        return u"<%s: %s/%s>" % (self.__class__.__name__,
                                 self.domain.name,
                                 self.name)

class User(DomainChild):
    """
    A Samba domain user
    """
    pass


class Group(DomainChild):
    """
    A Samba domain group
    """
    pass


class Alias(DomainChild):
    """
    A Samba domain alias
    """
    pass
