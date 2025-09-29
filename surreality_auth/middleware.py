"""
Shared authentication middleware for Python services.
Provides JWT validation and user account extraction using Supabase service role key.
"""

import os
import jwt
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

# HTTP Bearer token extraction
security = HTTPBearer()


class AuthMiddleware:
    """
    Authentication middleware for Python services using Supabase service role key.

    This middleware:
    1. Validates JWT tokens from requests
    2. Extracts account_id from validated tokens
    3. Uses Supabase service role key to bypass RLS
    4. Provides helper methods for authenticated database queries
    """

    def __init__(self):
        # Initialize Supabase client with service role key (bypasses RLS)
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

        if not all([self.supabase_url, self.service_role_key, self.jwt_secret]):
            raise ValueError(
                "Missing required environment variables: "
                "SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET"
            )

        # Create Supabase client with service role key
        self.supabase: Client = create_client(self.supabase_url, self.service_role_key)

    async def get_current_account_id(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> str:
        """
        Extract and verify account_id from JWT token.

        Args:
            credentials: HTTP Bearer token from request

        Returns:
            account_id: User's account UUID

        Raises:
            HTTPException: If token is invalid or missing account_id
        """
        token = credentials.credentials

        try:
            # Verify and decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                audience="authenticated"
            )

            # Extract account_id from token (try both 'sub' and 'account_id' fields)
            account_id = payload.get("sub") or payload.get("account_id")

            if not account_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token: missing account_id"
                )

            # Validate account_id format (should be UUID)
            if not self._is_valid_uuid(account_id):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token: malformed account_id"
                )

            return account_id

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

    def get_service_supabase(self) -> Client:
        """
        Get Supabase client with service role key.

        Returns:
            Client: Supabase client that bypasses RLS

        Note:
            Since this uses service role key, RLS is bypassed.
            You MUST manually filter queries by account_id.
        """
        return self.supabase

    async def verify_account_exists(self, account_id: str) -> bool:
        """
        Verify that an account_id exists in the users table.

        Args:
            account_id: User's account UUID

        Returns:
            bool: True if account exists, False otherwise
        """
        try:
            result = self.supabase.table("users")\
                .select("account_id")\
                .eq("account_id", account_id)\
                .limit(1)\
                .execute()

            return len(result.data) > 0

        except Exception:
            return False

    async def get_user_info(self, account_id: str) -> Optional[dict]:
        """
        Get user information for an account_id.

        Args:
            account_id: User's account UUID

        Returns:
            dict: User information or None if not found
        """
        try:
            result = self.supabase.table("users")\
                .select("*")\
                .eq("account_id", account_id)\
                .single()\
                .execute()

            return result.data

        except Exception:
            return None

    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """
        Validate UUID format.

        Args:
            uuid_string: String to validate as UUID

        Returns:
            bool: True if valid UUID format
        """
        try:
            import uuid
            uuid.UUID(uuid_string)
            return True
        except (ValueError, TypeError):
            return False


# Global instance for easy import
auth_middleware = AuthMiddleware()


# Convenience dependency functions
async def require_auth(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    Convenience function to get current account_id from JWT.
    Use this as a FastAPI dependency.

    Example:
        @app.get("/messages")
        async def get_messages(account_id: str = Depends(require_auth)):
            # Use account_id to filter queries
            pass
    """
    return await auth_middleware.get_current_account_id(credentials)


def get_service_supabase() -> Client:
    """
    Convenience function to get Supabase service client.

    Returns:
        Client: Supabase client with service role key (bypasses RLS)

    Example:
        supabase = get_service_supabase()
        # IMPORTANT: Must manually filter by account_id
        messages = supabase.table("messages")\\
            .select("*")\\
            .eq("account_id", account_id)\\
            .execute()
    """
    return auth_middleware.get_service_supabase()