from typing import cast

from fastapi import APIRouter, FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

swagger_router = APIRouter(
    tags=["swagger"],
    responses={404: {"description": "Not found"}, 401: {"description": "未提供TOKEN"}},
)

fast_api_swagger = FastAPI()


@swagger_router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义Swagger UI HTML"""
    return get_swagger_ui_html(
        openapi_url=cast(str, fast_api_swagger.openapi_url),
        title=fast_api_swagger.title + " - Swagger UI",
        oauth2_redirect_url=fast_api_swagger.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/image.png",
    )


@swagger_router.get(
    cast(str, fast_api_swagger.swagger_ui_oauth2_redirect_url), include_in_schema=False
)
async def swagger_ui_redirect():
    """Swagger UI OAuth2重定向HTML"""
    return get_swagger_ui_oauth2_redirect_html()


@swagger_router.get("/redoc", include_in_schema=False)
async def redoc_html():
    """自定义ReDoc HTML"""
    return get_redoc_html(
        openapi_url=cast(str, fast_api_swagger.openapi_url),
        title=fast_api_swagger.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )
