import jwt
from typing import Annotated, Any
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import HTTPException
from fastapi import Request, status
'''
JWT verifier : verifies the jwt token of the incoming request
whichever endpoints require so, verifies expiration time,
verifies role and if everythings correct, it extracts the payload and returns it
'''
security = HTTPBearer(auto_error=False)

def verifyJWTandGetUser( allowed_roles: list[str]):
    async def verifier(req: Request,
              credentials: Annotated[HTTPAuthorizationCredentials | None, Security(security)]
    ) -> dict[str, Any]:
    
        if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"status": "error", "message": "Missing Authorization header."},
                    headers={"WWW-Authenticate": "Bearer"},
                )

        try:
            config = req.app.state.config
            payload = jwt.decode(
                credentials.credentials,
                config.jwt_key,
                algorithms=[config.jwt_hash_algo],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["exp", "sub","role"],
                },
            )
                
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"status": "Unauthorized Access", "message": "Expired Token."},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"status": "Unauthorized Access", "message": "Invalid token signature."},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"status": "Unauthorized Access", "message": "Malformed/Invalid token."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        if payload["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"status": "Forbidden Access", "message": "This user is not permitted to avail this service."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    return verifier
            