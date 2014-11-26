from pydentity.samba_util import SECURITY_FLAG

class PolicyHandleObject(object):
    """
    Mixin for objects that have policy_handle objects associated with them
    """
    _policy_handle_obj = None

    @property
    def samr_handle(self):
        """
        SAMRHandle used to retrieve this object
        """
        raise NotImplementedError("Must override samr_handle")

    @property
    def parent_handle(self):
        """
        Parent policy_handle object
        """
        raise NotImplementedError("Must override parent_handle")

    @property
    def canonical_id(self):
        """
        The RID/SID/<X>ID for this object
        """
        raise NotImplementedError("Must override canonical_id")

    @property
    def policy_handle_obj(self):
        """
        Samba policy_handle object
        """
        if not self._policy_handle_obj:
            self._policy_handle_obj = getattr(
                self.samr_handle.connection_obj,
                'Open%s' % self.__class__.__name__,
            )(
                self.parent_handle,
                SECURITY_FLAG,
                self.canonical_id,
            )

        return self._policy_handle_obj


class Domain(PolicyHandleObject):
    """
    A Samba domain
    """
    _sid_obj = None

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
        return self._samr_handle
    @property
    def parent_handle(self):
        return self.samr_handle.policy_handle_obj
    @property
    def canonical_id(self):
        return self.sid_obj

    @property
    def sid_obj(self):
        """
        Samba dom_sid object
        """
        if not self._sid_obj:
            self._sid_obj = self.samr_handle.get_domain_sid_obj(self.name)

        return self._sid_obj

    @property
    def users(self):
        """
        List of users associated with this domain
        """
        return User.all_in_domain(self)

    def users_iter(self, rid=None):
        """
        Iterator for users associated with this domain, starting after the
        given RID
        """
        return User.all_in_domain_iter(self, rid)

    @property
    def groups(self):
        """
        List of groups associated with this domain
        """
        return Group.all_in_domain(self)

    def groups_iter(self, rid=None):
        """
        Iterator for groups associated with this domain, starting after the
        given RID
        """
        return Group.all_in_domain_iter(self, rid)

    @property
    def aliases(self):
        """
        List of aliases associated with this domain
        """
        return Alias.all_in_domain(self)

    def aliases_iter(self, rid=None):
        """
        Iterator for aliases associated with this domain, starting after the
        given RID
        """
        return Alias.all_in_domain_iter(self, rid)

    def __repr__(self):
        return self.__unicode__()
    def __unicode__(self):
        return u"<%s: %s>" % (self.__class__.__name__, self.name)


class DomainChild(PolicyHandleObject):
    """
    Base class for domain children
    """
    def __init__(self, domain, name, rid):
        self._domain = domain
        self._name = name
        self._rid = rid

    @classmethod
    def plural_name(cls):
        return "%ss" % cls.__name__

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

    @property
    def samr_handle(self):
        return self.domain.samr_handle
    @property
    def parent_handle(self):
        return self.domain.policy_handle_obj
    @property
    def canonical_id(self):
        return self.rid

    @classmethod
    def _domain_enum(cls, enum_func, domain, resume_handle=0, size=-1):
        """
        Low level wrapper around enumeration of domain children
        """
        return enum_func(domain.policy_handle_obj, resume_handle, size)

    @classmethod
    def _domain_enum_func(cls, samr_handle):
        """
        Low level domain enumeration function for this type
        """
        return getattr(samr_handle.connection_obj,
                       'EnumDomain%s' % cls.plural_name())


    @classmethod
    def all_in_domain(cls, domain):
        """
        Gets all objects of this type in the given domain
        """
        # EnumDomain{X} returns (resume handle, array obj, count)
        sam_array = cls._domain_enum(
            cls._domain_enum_func(domain.samr_handle), domain,
        )[1]

        return [
            cls(domain, entry.name.string, entry.idx)
            for entry in sam_array.entries
        ]

    @classmethod
    def all_in_domain_iter(cls, domain, resume_handle=None):
        """
        Gets objects after the given RID (resume_handle) of this type in the
        given domain, as an iterator
        """
        while resume_handle or resume_handle is None:
            # First iter default arg
            if resume_handle is None:
                resume_handle = 0

            resume_handle, entries_obj, count = cls._domain_enum(
                cls._domain_enum_func(domain.samr_handle),
                domain,
                resume_handle,
                1,
            )

            assert count <= 1, "No more than 1 object retrieved"

            if count == 1:
                entry_obj = entries_obj.entries.pop()
                yield cls(domain, entry_obj.name.string, entry_obj.idx)

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
    @classmethod
    def _domain_enum(cls, enum_func, domain, resume_handle=0, size=-1):
        # user takes an additional arg
        return enum_func(domain.policy_handle_obj, resume_handle, 0, size)


class Group(DomainChild):
    """
    A Samba domain group
    """
    pass


class Alias(DomainChild):
    """
    A Samba domain alias
    """
    @classmethod
    def plural_name(cls):
        return "Aliases"
