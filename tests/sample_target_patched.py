import json
import hmac
import hashlib
import base64

class SessionStateError(Exception):
    pass


class SessionStateLoader:
    def __init__(self, secret_key: bytes):
        if not isinstance(secret_key, (bytes, bytearray)) or len(secret_key) < 32:
            raise ValueError("secret_key must be at least 32 bytes")
        self._secret_key = bytes(secret_key)

    def load_session_state(self, raw_payload):
        """
        Safely deserialize session state from a signed, base64-encoded JSON payload.

        Expected format: base64url(hmac_sha256(payload) + b"." + payload)
        where payload is UTF-8 encoded JSON.

        Raises SessionStateError on any integrity or parsing failure.
        """
        if not isinstance(raw_payload, (str, bytes, bytearray)):
            raise SessionStateError("raw_payload must be str or bytes")

        if isinstance(raw_payload, str):
            try:
                raw_bytes = raw_payload.encode("ascii")
            except UnicodeEncodeError as exc:
                raise SessionStateError("raw_payload is not valid base64") from exc
        else:
            raw_bytes = bytes(raw_payload)

        try:
            decoded = base64.urlsafe_b64decode(raw_bytes + b"=" * (-len(raw_bytes) % 4))
        except (ValueError, base64.binascii.Error) as exc:
            raise SessionStateError("invalid base64 encoding") from exc

        if b"." not in decoded:
            raise SessionStateError("malformed payload: missing signature separator")

        signature, _, payload = decoded.partition(b".")

        expected_sig = hmac.new(self._secret_key, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_sig):
            raise SessionStateError("signature verification failed")

        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SessionStateError("payload is not valid UTF-8") from exc

        try:
            state = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SessionStateError("payload is not valid JSON") from exc

        if not isinstance(state, dict):
            raise SessionStateError("session state must be a JSON object")

        return state

if __name__ == '__main__':
    import os
    key = os.urandom(32)
    loader = SessionStateLoader(key)
    payload = b'{"user": "test_user", "role": "admin"}'
    sig = hmac.new(key, payload, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(sig + b'.' + payload)
    res = loader.load_session_state(token)
    assert res['user'] == 'test_user'
    print('[Sandbox Test] Güvenli JSON oturum doğrulama testi başarılı:', res)
