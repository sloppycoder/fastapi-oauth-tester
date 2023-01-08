import os

import jwt
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Security
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, SecurityScopes
from fastapi.security.http import HTTPAuthorizationCredentials
from jwt.exceptions import DecodeError, PyJWKClientError
from starlette.status import HTTP_403_FORBIDDEN


class TokenVerifier:
    def __init__(self):
        self.config = {
            "jwks_url": os.environ["JKWS_URL"],
            "audience": os.environ["TOKEN_AUDIENCE"],
            "algorithm": os.environ["TOKEN_ALGORITHM"],
            "issuer": os.environ["TOKEN_ISSUER"],
        }
        self.jwks_client = jwt.PyJWKClient(self.config["jwks_url"])

    def verify(self, token: str) -> dict:
        self.signing_key = self.jwks_client.get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            self.signing_key,
            algorithms=self.config["algorithm"],
            audience=self.config["audience"],
            issuer=self.config["issuer"],
        )


load_dotenv()

token_auth_scheme = HTTPBearer()
verifier = TokenVerifier()
app = FastAPI()


async def verify_token_scope(scopes: SecurityScopes, token: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    try:
        token_content = verifier.verify(token.credentials)
        token_scopes = set(token_content["scope"].split(" "))
        required_scopes = set(scopes.scopes)
        if token_scopes.issuperset(required_scopes):
            return token_content
        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="access token does not have the right scope",
            )
    except (DecodeError, PyJWKClientError) as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=f"invalid token: {e}")


@app.get("/api/public")
async def public_api():
    return {
        "status": "success",
        "msg": ("Hello from a public endpoint! You don't need to be " "authenticated to see this."),
    }


@app.get("/api/admin")
async def admin_api(current_user=Security(verify_token_scope, scopes=["admin:all"])):
    return current_user


@app.get("/api/customer")
async def customer_api(current_user=Security(verify_token_scope, scopes=["login:all"])):
    return current_user


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
