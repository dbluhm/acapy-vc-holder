"""KMS Suite Provider."""

from datetime import datetime
import logging
from typing import List, Optional

from aries_cloudagent.core.profile import Profile
from aries_cloudagent.utils.multiformats import multibase
from aries_cloudagent.vc.ld_proofs import (
    DocumentLoaderMethod,
    LinkedDataProof,
    LinkedDataSignature,
)
from aries_cloudagent.vc.vc_ld.external_suite import (
    ExternalSuiteNotFoundError,
    ExternalSuiteProvider,
)
from aries_cloudagent.wallet.default_verification_key_strategy import (
    BaseVerificationKeyStrategy,
    DefaultVerificationKeyStrategy,
)
from aries_cloudagent.wallet.did_info import DIDInfo
from aries_cloudagent.wallet.key_type import KeyType
from did_peer_4 import resolve

from acapy_vc_holder.kms import MiniKMS


LOGGER = logging.getLogger(__name__)


class KMSVerificationKeyStrategy(BaseVerificationKeyStrategy):
    """KMS Verification Key Strategy."""

    def __init__(self):
        """Initialize the strategy."""
        self.fallback = DefaultVerificationKeyStrategy()

    async def get_verification_method_id_for_did(
        self,
        did: str,
        profile: Optional[Profile],
        allowed_verification_method_types: Optional[List[KeyType]] = None,
        proof_purpose: Optional[str] = None,
    ) -> Optional[str]:
        """Get the verification method ID for the DID."""
        if did.startswith("did:peer:4"):
            doc = resolve(did)
            if (am := doc.get("assertionMethod")) and len(am) > 0:
                return did + am[0]

        return await self.fallback.get_verification_method_id_for_did(
            did, profile, allowed_verification_method_types, proof_purpose
        )


class KMSEd25519Suite(LinkedDataSignature):
    """KMS Suite."""

    signature_type = "Ed25519Signature2020"

    def __init__(
        self,
        client: MiniKMS,
        verification_method: str,
        *,
        proof: Optional[dict] = None,
        date: Optional[datetime] = None,
    ):
        """Initialize the suite."""
        super().__init__(
            proof=proof, verification_method=verification_method, date=date
        )
        LOGGER.debug(
            "KMS Suite initialized with: proof: %s, vm: %s",
            proof,
            verification_method,
        )
        self.client = client
        self.verification_method = verification_method

    async def sign(self, *, verify_data: bytes, proof: dict) -> dict:
        """Sign the value."""
        key = await self.client.get_key_by_alias(self.verification_method)
        sig = await self.client.sign(key.kid, verify_data)
        proof["proofValue"] = multibase.encode(sig, "base58btc")
        LOGGER.debug("KMS Suite signed proof: %s", proof)
        return proof

    async def verify_signature(
        self,
        *,
        verify_data: bytes,
        verification_method: dict,
        document: dict,
        proof: dict,
        document_loader: DocumentLoaderMethod,
    ) -> bool:
        """Verify the signature."""
        raise NotImplementedError("Verification not supported by KMS")


class KmsSuiteProvider(ExternalSuiteProvider):
    """KMS Suite Provider."""

    def __init__(self, client: MiniKMS):
        """Initialize the suite provider."""
        self.client = client

    async def get_suite(
        self,
        profile: Profile,
        proof_type: str,
        proof: dict,
        verification_method: str,
        did_info: DIDInfo,
    ) -> Optional[LinkedDataProof]:
        """Get the suite."""
        if proof_type != "Ed25519Signature2020":
            raise ExternalSuiteNotFoundError("Unsupported proof type: " + proof_type)

        wallet_id = profile.settings.get_str("wallet.id")
        if wallet_id:
            client = self.client.with_profile(wallet_id)
        else:
            client = self.client

        return KMSEd25519Suite(
            client,
            verification_method=verification_method,
            proof=proof,
        )
