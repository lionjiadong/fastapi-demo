import re

from fastapi import HTTPException, status


def integrityError_exception(error: str) -> HTTPException:
    search = re.search(r"DETAIL:\s*(.*)", error)
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{search.group(1) if search else error}",
    )
