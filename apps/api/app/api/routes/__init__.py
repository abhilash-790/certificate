from fastapi import APIRouter
from app.api.routes import health, auth, certificates, issuer, public, review

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(certificates.router)
api_router.include_router(issuer.router)
api_router.include_router(public.router)
api_router.include_router(review.router)
