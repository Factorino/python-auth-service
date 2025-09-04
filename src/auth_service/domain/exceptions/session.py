class SessionNotFoundError(Exception):
    def __init__(self, session_id: str) -> None:
        super().__init__(f"Session with ID '{session_id}' not found")


class SessionRevokedError(Exception):
    def __init__(self, jti: str) -> None:
        super().__init__(f"Session with JTI '{jti}' has been revoked")
