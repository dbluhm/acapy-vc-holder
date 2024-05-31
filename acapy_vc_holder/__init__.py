"""acapy-vc-holder plugin init module."""

from os import getenv

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.config.provider import ClassProvider
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.storage.vc_holder.base import VCHolder

from .kms import MiniKMS
from .provider import ExternalVCHolder


async def setup(context: InjectionContext):
    """Setup plugin."""
    KMS_BASE_URL = getenv("KMS_BASE_URL")
    if not KMS_BASE_URL:
        raise ValueError("KMS_BASE_URL not set")

    kms_client = MiniKMS(base_url=KMS_BASE_URL)
    context.injector.bind_instance(MiniKMS, kms_client)

    context.injector.bind_provider(
        VCHolder,
        ClassProvider(
            ExternalVCHolder, profile=ClassProvider.Inject(Profile), kms=kms_client
        ),
    )
