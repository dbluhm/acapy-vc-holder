"""Routes for the external-vc-holder plugin."""

from aiohttp import web
from aiohttp_apispec import docs

from aries_cloudagent.admin.request_context import AdminRequestContext

from .kms import MiniKMS


@docs(tags=["external-vc-holder"], summary="Create a DID using the KMS")
async def setup_profile(request: web.Request):
    """Create DID."""
    context: AdminRequestContext = request["context"]
    client = context.inject(MiniKMS)
    wallet_id = context.settings.get_str("wallet.id")
    if wallet_id:
        await client.create_profile_if_not_exists(wallet_id)

    return web.json_response({})


async def register(app: web.Application):
    """Register routes."""
    app.add_routes(
        [
            web.post("/ext/profile/setup", setup_profile),
        ]
    )


def post_process_routes(app: web.Application):
    """Amend swagger API."""
    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []

    app._state["swagger_dict"]["tags"].append(
        {
            "name": "external-vc-holder",
            "description": "external vc holder plugin",
        }
    )
