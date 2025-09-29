# Surreality Auth

Shared authentication middleware for Surreality AI services.

## Features

- JWT token validation using Supabase
- Account-based access control
- FastAPI dependency injection support
- Service role key authentication
- Account ID extraction from JWT tokens

## Installation

```bash
pip install surreality-auth
```

## Usage

### Python/FastAPI Services

```python
from surreality_auth import AuthMiddleware, require_auth

# Initialize auth middleware
auth = AuthMiddleware()

# Use as FastAPI dependency
@app.get("/protected")
async def protected_endpoint(account_id: str = Depends(auth.get_current_account_id)):
    return {"account_id": account_id}

# Or use the convenience decorator
@app.get("/also-protected")
async def also_protected(account_id: str = Depends(require_auth)):
    return {"account_id": account_id}
```

### Environment Variables

Required environment variables:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for authentication
- `SUPABASE_JWT_SECRET`: JWT secret for token validation

## License

MIT License