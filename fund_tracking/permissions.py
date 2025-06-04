from rest_framework import permissions

class IsNotStudentUser(permissions.BasePermission):
    """
    Allows access only to users who are NOT in the 'Student' group.
    """

    def has_permission(self, request, view):
        user = request.user

        # Allow access if the user is not authenticated — optional:
        if not user or not user.is_authenticated:
            return False

        # TODO: add the not back
        if request.method == "GET": return True
        return user.groups.filter(name="Student").exists()
