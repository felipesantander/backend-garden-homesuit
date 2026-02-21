import logging

from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from core.models import Role

logger = logging.getLogger(__name__)

class RBACMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Skip RBAC for non-API endpoints, admin, and token endpoints
        if not request.path.startswith("/api/") or \
           request.path.startswith("/api/token/") or \
           request.path.startswith("/api/ingest/") or \
           request.path.startswith("/admin/"):
            return self.get_response(request)

        # 2. Authenticate the request using SimpleJWT
        try:
            header = JWTAuthentication().get_header(request)
            if header is None:
                return JsonResponse({"error": "Authentication credentials were not provided."}, status=401)

            raw_token = JWTAuthentication().get_raw_token(header)
            if raw_token is None:
                return JsonResponse({"error": "Invalid token header."}, status=401)

            validated_token = JWTAuthentication().get_validated_token(raw_token)
            role_name = validated_token.get("role")

            if not role_name:
                return JsonResponse({"error": "No role found in token payload."}, status=403)

        except (InvalidToken, TokenError) as e:
             return JsonResponse({"error": str(e)}, status=401)
        except Exception as e:
            logger.error(f"RBAC Middleware Auth Error: {e}")
            return JsonResponse({"error": "Authentication failed."}, status=401)

        # 3. Check permissions for the role
        try:
            role = Role.objects.get(name=role_name)
            current_path = request.path
            current_method = request.method
            current_host = request.get_host()

            is_authorized = False
            for permission in role.permissions.all():
                for endpoint in permission.endpoints:
                    # endpoint is {path, host, method}
                    # We can use simple string matching or regex if needed later
                    endpoint_path = endpoint.get("path")
                    if endpoint_path.endswith("*"):
                        base_path = endpoint_path[:-1]
                        path_match = current_path.startswith(base_path)
                    else:
                        path_match = current_path == endpoint_path or \
                                     (endpoint_path.endswith("/") and current_path == endpoint_path[:-1]) or \
                                     (not endpoint_path.endswith("/") and current_path == endpoint_path + "/")

                    method_match = endpoint.get("method") == current_method or endpoint.get("method") == "*"
                    host_match = endpoint.get("host") == current_host or endpoint.get("host") == "*"

                    if path_match and method_match and host_match:
                        # Scoping Check
                        allowed_gardens = permission.gardens
                        allowed_businesses = permission.businesses
                        allowed_machines = permission.machines

                        path_parts = [p for p in current_path.split("/") if p]

                        # Scoping logic: if a scope is defined (not empty), the resource ID must be in it
                        if allowed_gardens and "gardens" in path_parts:
                            idx = path_parts.index("gardens")
                            if len(path_parts) > idx + 1:
                                if path_parts[idx + 1] not in allowed_gardens:
                                    continue
                        
                        if allowed_businesses and "businesses" in path_parts:
                            idx = path_parts.index("businesses")
                            if len(path_parts) > idx + 1:
                                if path_parts[idx + 1] not in allowed_businesses:
                                    continue

                        if allowed_machines and "machines" in path_parts:
                            idx = path_parts.index("machines")
                            if len(path_parts) > idx + 1:
                                if path_parts[idx + 1] not in allowed_machines:
                                    continue

                        is_authorized = True
                        break
                if is_authorized:
                    break

            if not is_authorized:
                logger.warning(f"Access denied for role '{role_name}' to {current_method} {current_path} on host {current_host}")
                return JsonResponse({"error": f"Role '{role_name}' does not have permission for this endpoint."}, status=403)

        except Role.DoesNotExist:
            return JsonResponse({"error": f"Role '{role_name}' defined in token does not exist."}, status=403)
        except Exception as e:
            logger.error(f"RBAC Middleware Permission Check Error: {e}")
            return JsonResponse({"error": "Internal server error during authorization check."}, status=500)

        return self.get_response(request)
