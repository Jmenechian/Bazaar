from fastapi import Header, HTTPException, Depends


def verify_token(authorization: str = Header(None)):
    """
    Extract and verify the JWT bearer token from the Authorization header.
    Returns the authenticated user_id if valid.
    TODO: Implement JWT decoding and signature verification.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    # TODO: Implement token verification logic
    pass
