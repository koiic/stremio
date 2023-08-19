from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self, item: str):
        detail = f"{item} not found"
        super().__init__(status_code=404, detail=detail)


class BadRequestException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)


class UnauthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Unauthorized")


class ForbiddenException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=403, detail=message)
