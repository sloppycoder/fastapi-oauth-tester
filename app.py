import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from security import TokenVerifier

load_dotenv()

token_auth_scheme = HTTPBearer()

app = FastAPI()


@app.get("/api/public")
async def public():
    return {
        "status": "success",
        "msg": ("Hello from a public endpoint! You don't need to be " "authenticated to see this."),
    }


@app.get("/api/private")
async def private(token: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    """A valid access token is required to access this route"""

    return TokenVerifier().verify(token.credentials)


# run uvicorn app:app --reload
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
