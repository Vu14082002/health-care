import functools
from dataclasses import dataclass
from typing import Any, List

from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

Allow: str = "allow"
Deny: str = "deny"


@dataclass(frozen=True)
class Principal:
    key: str
    value: str

    def __repr__(self) -> str:
        """
         Returns a string representation of the key - value pair. This is useful for debugging the object's __repr__ method.
         
         
         @return A string representation of the key - value pair in the form key : value or key : value if there is no
        """
        return f"{self.key}:{self.value}"

    def __str__(self) -> str:
        """
         Returns a string representation of the object. This is useful for debugging purposes. The string representation can be accessed using the __repr__ method.
         
         
         @return A string representation of the object or None if the object is not a string or None is passed to __
        """
        return self.__repr__()


@dataclass(frozen=True)
class SystemPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        """
         Initialize the class with a value. This is a wrapper around __init__ to allow subclasses to define their own initialization logic
         
         @param value - The value to set for the property
         
         @return The instance of the class that was initialized with the value passed in as the first argument ( if any
        """
        super().__init__(key="system", value=value, *args, **kwargs)


@dataclass(frozen=True)
class UserPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        """
         Initialize the object with the value. This is a wrapper around __init__ to allow subclasses to initialize their own values before they are passed to the constructor
         
         @param value - The value to set for the object
         
         @return The object that was initialized with the value or None if it couldn't be initialized due to an
        """
        super().__init__(key="user", value=value, *args, **kwargs)


@dataclass(frozen=True)
class RolePrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        """
         Initialize the class with a value. This is a wrapper around __init__ to allow subclasses to initialize their own attributes and to provide an easy way to pass values to the constructor
         
         @param value - The value to set for the attribute
         
         @return The instance of the class to be used in the test harness or None if it can't be
        """
        super().__init__(key="role", value=value, *args, **kwargs)


@dataclass(frozen=True)
class ItemPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        """
         Initialize a : class : ` PlexItem `. This is a convenience method for : meth : ` __init__ ` with the exception that it will set the key " item " to the value of the argument.
         
         @param value - The value to set. This can be a string or a list of strings.
         
         @return The newly created : class : ` PlexItem ` or None if the argument was invalid. >>> item = PlexItem ( " a " )
        """
        super().__init__(key="item", value=value, *args, **kwargs)


@dataclass(frozen=True)
class ActionPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        """
         Initialize the instance. This is a wrapper around the __init__ method to provide the key " action " and value for the instance
         
         @param value - The value of the instance
         
         @return The instance that was created or None if it couldn't be created for some reason ( not all
        """
        super().__init__(key="action", value=value, *args, **kwargs)


Everyone = SystemPrincipal(value="everyone")
Authenticated = SystemPrincipal(value="authenticated")


class AllowAll:
    def __contains__(self, item: Any) -> bool:
        """
         Checks if the item is contained in the list. This is used to implement __contains__ in order to avoid having to reimplement it every time it is accessed
         
         @param item - The item to check for
         
         @return True if the item is contained False if it is not and exception is raised if the item is not
        """
        return True

    def __repr__(self) -> str:
        """
         Returns a string representation of the class. This is useful for debugging the class as it can be printed to the console without having to reimplement __repr__.
         
         
         @return A string representation of the class ( including spaces ). >>> class A : def __repr__ ( self ) : return " *
        """
        return "*"

    def __str__(self) -> str:
        """
         Returns a string representation of the object. This is useful for debugging purposes. The string representation can be accessed using the __repr__ method.
         
         
         @return A string representation of the object or None if the object is not a string or None is passed to __
        """
        return self.__repr__()


default_exception = HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")


class AccessControl:
    def __init__(
        self,
        user_principals_getter: Any,
        permission_exception: Any = default_exception,
    ) -> None:
        self.user_principals_getter = user_principals_getter
        self.permission_exception = permission_exception

    def __call__(self, permissions: str):
        """
         Creates a function that checks if the user has the given permissions. The permission is passed to the function as a string of comma separated permission names
         
         @param permissions - A list of comma separated permission names
         
         @return A function that checks if the user has the given permissions. If the user does not have the permissions raises
        """
        def _permission_dependency(principals=self.user_principals_getter()):
            """
             Returns a function that checks if the user has the right permissions. This is used to ensure that permissions are checked in the context of a test.
             
             @param principals - A list of principals that should be checked.
             
             @return A function that takes a list of principals and returns True if the user has the right permissions False otherwise
            """
            assert_access = functools.partial(
                self.assert_access, principals, permissions
            )
            return assert_access

        return _permission_dependency

    def assert_access(self, principals: list, permissions: str, resource: Any):
        """
         Assert that the user has the required permissions. This is a convenience method for : meth : ` has_permission `
         
         @param principals - List of principals to check.
         @param permissions - List of permissions to check. If empty all permissions are checked.
         @param resource - The resource for which the permissions are checked. It can be a string or a : class : ` fatiando. resource. Resource `
        """
        # Returns True if the user has the permission to perform the given permission.
        if not self.has_permission(
            principals=principals,
            required_permissions=permissions,
            resource=resource,
        ):
            raise self.permission_exception

    def has_permission(
        self, principals: List[Principal], required_permissions: str, resource: Any
    ):
        """
         Checks if principals have permission to access resource. This is a helper method for : meth : ` get_acl `.
         
         @param principals - List of principals to check. Can be None for anonymous users
         @param required_permissions - String or list of strings specifying the permissions that must be granted.
         @param resource - A resource or list of resources to check.
         
         @return True if all principals have permission False otherwise. Example usage :. from owlmixin import Access control >>> access = Access. objects. has_permission ( ['admin'' read'] ['group '
        """
        # If resource is a list it will be converted to a list of resource objects.
        if not isinstance(resource, list):
            resource = [resource]

        permits = []
        # Returns true if the resource has granted permissions.
        for resource_obj in resource:
            granted = False
            acl = self._acl(resource_obj)
            # If required_permissions is a list of permissions to be checked for the user.
            if not isinstance(required_permissions, list):
                required_permissions = [required_permissions]

            # Check if the action principal permission is allowed to be granted.
            for action, principal, permission in acl:
                is_required_permissions_in_permission = any(
                    required_permission in permission
                    for required_permission in required_permissions
                )

                # If the action is Allow or Everyone then the permission is granted.
                if (action == Allow and is_required_permissions_in_permission) and (
                    principal in principals or principal == Everyone
                ):
                    granted = True
                    break

            permits.append(granted)

        return all(permits)

    def show_permissions(self, principals: List[Principal], resource: Any):
        """
         Get the permissions for a list of principals. This is a helper method for get_permissions_for_resource.
         
         @param principals - A list of principals to check. Can be None if no principals are allowed.
         @param resource - A resource or list of resources. Can be None if no resources are allowed.
         
         @return A list of permissions that apply to the resource ( s ). Each permission is a tuple of ( action principal_name
        """
        # If resource is a list it will be converted to a list of resource objects.
        if not isinstance(resource, list):
            resource = [resource]

        permissions = []
        # Returns a list of permissions for all the permissions in the resource.
        for resource_obj in resource:
            local_permissions = []
            acl = self._acl(resource_obj)

            # Add permission to local_permissions list
            for action, principal, permission in acl:
                # Add permission to local_permissions list
                if action == Allow and principal in principals or principal == Everyone:
                    local_permissions.append(permission)

            permissions.append(local_permissions)

        # get intersection of permissions
        permissions = [self._flatten(permission) for permission in permissions]
        permissions = functools.reduce(set.intersection, map(set, permissions))

        return list(permissions)

    def _acl(self, resource):
        """
         Return the ACL for a resource. This is a helper to allow subclasses to override the behavior of ACLs.
         
         @param resource - The resource to get the ACL for. Can be a : class : ` Resource ` or a callable that returns a list of ACLs.
         
         @return A list of ACLs or a callable that returns a list of ACLs if there is no ACL
        """
        acl = getattr(resource, "__acl__", [])
        # Returns the acl function if callable acl.
        if callable(acl):
            return acl()
        return acl

    def _flatten(self, any_list: List[Any]) -> List[Any]:
        """
         Flatten a list of nested lists. This is used to flatten the data structure that we are going to pass to : meth : ` _get_data `
         
         @param any_list - The list to flatten.
         
         @return A list of flattened data structures for the list passed to : meth : ` _get_data `
        """
        flat_list = []
        # Flatten all the elements of any_list.
        for element in any_list:
            # Flatten the given element to a flat list.
            if isinstance(element, list):
                flat_list += self._flatten(element)
            else:
                flat_list.append(element)
        return flat_list
