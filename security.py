import os

import jwt
from jwt.exceptions import DecodeError, PyJWKClientError


class TokenVerifier:
    def __init__(self):
        self.config = {
            "jwks_url": os.environ["JKWS_URL"],
            "audience": os.environ["TOKEN_AUDIENCE"],
            "algorithm": os.environ["TOKEN_ALGORITHM"],
            "issuer": os.environ["TOKEN_ISSUER"],
        }
        self.jwks_client = jwt.PyJWKClient(self.config["jwks_url"])

    def verify(self, token: str):
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(token).key
        except (PyJWKClientError, DecodeError) as error:
            return {"status": "error", "msg": str(error)}

        try:
            return jwt.decode(
                token,
                self.signing_key,
                algorithms=self.config["algorithm"],
                audience=self.config["audience"],
                issuer=self.config["issuer"],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}
