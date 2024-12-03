from typing import Annotated
from fastapi_nextauth_jwt import NextAuthJWT
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from app.core.config import PROXY_PREFIX, api_same_origin

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["nextAuthJWT"],
)

JWT = NextAuthJWT(
    secret="y0uR_SuP3r_s3cr37_$3cr3t",
)

# /be/auth/token
@router.get("/auth/next/jwt")
async def return_jwt(jwt: Annotated[dict, Depends(JWT)]):
    return {"message": f"Hi {jwt['name']}. Greetings from fastapi!"}

# For CSRF protection testing
@router.post("/auth/next/jwt")
async def return_jwt(jwt: Annotated[dict, Depends(JWT)]):
    return {"message": f"Hi {jwt['name']}. Greetings from fastapi!"}