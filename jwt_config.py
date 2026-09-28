"""JWT verification settings shared by the hub and the demo backends.

Real setup: point these env vars at your identity provider and delete the demo key fallback:
    JWT_JWKS_URI=https://your-idp/.well-known/jwks.json
    JWT_ISSUER=https://your-idp/
    JWT_AUDIENCE=your-api-audience
Demo setup: a local RSA key pair in demo_keys/ signs and verifies test tokens.
"""
import os
from pathlib import Path

from fastmcp.server.auth.providers.jwt import JWTVerifier, RSAKeyPair
from pydantic import SecretStr

KEY_DIR = Path(__file__).parent / "demo_keys"
ISSUER = os.getenv("JWT_ISSUER", "https://demo-idp.local")
AUDIENCE = os.getenv("JWT_AUDIENCE", "mcp-hub-demo")


def demo_keypair() -> RSAKeyPair:
    """Create the demo key pair once, then reuse it so every process agrees on it."""
    priv, pub = KEY_DIR / "private.pem", KEY_DIR / "public.pem"
    if not priv.exists():
        KEY_DIR.mkdir(exist_ok=True)
        kp = RSAKeyPair.generate()
        priv.write_text(kp.private_key.get_secret_value())
        pub.write_text(kp.public_key)
    return RSAKeyPair(private_key=SecretStr(priv.read_text()), public_key=pub.read_text())


def verifier() -> JWTVerifier:
    if jwks := os.getenv("JWT_JWKS_URI"):
        return JWTVerifier(jwks_uri=jwks, issuer=ISSUER, audience=AUDIENCE)
    return JWTVerifier(public_key=demo_keypair().public_key, issuer=ISSUER, audience=AUDIENCE)


def mint_demo_token(user: str) -> str:
    """What your MCP host / IdP would normally hand out."""
    return demo_keypair().create_token(subject=user, issuer=ISSUER, audience=AUDIENCE)
