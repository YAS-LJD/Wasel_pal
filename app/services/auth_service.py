class AuthService:
    def login(self, email: str, password: str):
        return {"access_token": "token", "token_type": "bearer"}

    def register(self, payload: dict):
        return payload
