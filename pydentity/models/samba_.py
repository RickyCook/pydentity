import logging

from samba.dcerpc import lsa
from samba.dcerpc.samr import (
    ALIASINFOALL,
    DomainGeneralInformation,
    DomainGeneralInformation2,
    DomainModifiedInformation,
    DomainPasswordInformation,
    GROUPINFOALL,
    UserAllInformation,
)

from pydentity.samba_util import SECURITY_FLAG, lsa_unwrap
from pydentity.util import SYSTEM_PROPERTY_RE

class PolicyHandleObject(object):
    """
    Mixin for objects that have policy_handle objects associated with them
    """
    _policy_handle_obj = None
    _attrs = None

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
    def all_info_class_level(self):
        """
        The information class level to retrieve all info for this policy object
        """
        raise NotImplementedError("Must override all_info_class_level")

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

    @property
    def attrs(self):
        """
        Lazy loaded dict of the args from the policy object
        """
        if not self._attrs:
            request_levels = self.all_info_class_level
            if not isinstance(request_levels, (list, tuple)):
                request_levels = (request_levels,)

            attrs = {}
            for request_level in request_levels:
                info_obj = getattr(
                    self.samr_handle.connection_obj,
                    'Query%sInfo' % self.__class__.__name__,
                )(
                    self.policy_handle_obj,
                    request_level,
                )

                attrs.update({
                    attr_name: lsa_unwrap(getattr(info_obj, attr_name))
                    for attr_name in dir(info_obj)
                    if not SYSTEM_PROPERTY_RE.match(attr_name)
                })

            self._attrs = attrs

        return self._attrs

    @property
    def loaded(self):
        """
        Whether the attrs for this object have been loaded
        """
        return self._attrs is not None

    @property
    def name(self):
        """
        Standardized object name
        """
        return self.attrs['name']


class Domain(PolicyHandleObject):
    """
    A Samba domain
    """
    _sid_obj = None
    all_info_class_level = (
        DomainGeneralInformation,
        DomainGeneralInformation2,
        DomainModifiedInformation,
        DomainPasswordInformation,
    )

    def __init__(self, name, samr_handle):
        self._name = name
        self._samr_handle = samr_handle

    @property
    def name(self):
        if self.loaded:
            return self.attrs['domain_name']

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
    name_attr = 'name'

    def __init__(self, domain, rid, name=None):
        self._domain = domain
        self._rid = rid
        self._name = name

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
        if self._name and not self.loaded:
            return self._name

        return self.attrs[self.name_attr]

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
            cls(domain, entry.idx, name=lsa_unwrap(entry.name))
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
                entry = entries_obj.entries.pop()
                yield cls(domain, entry.idx, name=lsa_unwrap(entry.name))

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
    all_info_class_level = UserAllInformation
    name_attr = 'account_name'

    @classmethod
    def _domain_enum(cls, enum_func, domain, resume_handle=0, size=-1):
        # user takes an additional arg
        return enum_func(domain.policy_handle_obj, resume_handle, 0, size)


class Group(DomainChild):
    """
    A Samba domain group
    """
    all_info_class_level = GROUPINFOALL


class Alias(DomainChild):
    """
    A Samba domain alias
    """
    all_info_class_level = ALIASINFOALL

    @classmethod
    def plural_name(cls):
        return "Aliases"
