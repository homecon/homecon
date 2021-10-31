from homecon.core.auth import AuthManager


class TestAuthManager:
    def test_token_encode_decode(self):
        manager = AuthManager()
        token = manager.create_token(allowed_event_types=['test', 'update'])

        assert manager.is_authorized('test', {}, token)
        assert manager.is_authorized('update', {}, token)
        assert not manager.is_authorized('random', {}, token)
