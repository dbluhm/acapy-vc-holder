"""External VC Holder Provider."""

import logging
from typing import Any, List, Mapping, Optional, Sequence

from aries_cloudagent.core.profile import Profile
from aries_cloudagent.storage.vc_holder.askar import AskarVCHolder
from aries_cloudagent.storage.vc_holder.base import VCRecord, VCRecordSearch

from acapy_vc_holder.kms import MiniKMS


LOGGER = logging.getLogger(__name__)


class ExternalVCRecordSearch(VCRecordSearch):
    """VC Record Search for external VC Holder."""

    def __init__(
        self, kms: MiniKMS, search_params: Mapping[str, Any], default_page_size: int = 20
    ):
        """Initiliaze the search."""
        self.kms = kms
        self.params = search_params
        self.page_size = default_page_size
        self.offset = 0
        self.results: List[VCRecord] = []

    async def close(self):
        """Close the search."""
        self.results.clear()

    async def fetch(self, max_count: Optional[int] = None) -> Sequence[VCRecord]:
        """Fetch the next batch of records."""
        limit = max_count or self.page_size
        records = await self.kms.search_credentials(
            **self.params,
            offset=self.offset,
            limit=limit,
        )
        self.offset = self.offset + len(records) - 1
        return records


class ExternalVCHolder(AskarVCHolder):
    """External VC Record storage using mini-kms."""

    def __init__(self, profile: Profile, kms: MiniKMS):
        """Initialize holder."""
        wallet_id = profile.settings.get_str("wallet.id")
        self.kms = kms.with_profile(wallet_id)

    async def store_credential(self, cred: VCRecord):
        """Add a new VC record to the external store."""
        await self.kms.store_credential(cred)

    async def retrieve_credential_by_id(self, record_id: str) -> VCRecord:
        """Retrieve a credential by id."""
        return await self.kms.retrieve_credential_by_id(record_id)

    async def retrieve_credential_by_given_id(self, given_id: str) -> VCRecord:
        """Retrieve a credential by given id."""
        return await self.kms.retrieve_credential_by_given_id(given_id)

    async def delete_credential(self, cred: VCRecord):
        """Delete a credential."""
        return await self.kms.delete_credential(cred.record_id)

    def search_credentials(
        self,
        contexts: Sequence[str] = None,
        types: Sequence[str] = None,
        schema_ids: Sequence[str] = None,
        issuer_id: str = None,
        subject_ids: str = None,
        proof_types: Sequence[str] = None,
        given_id: str = None,
        tag_query: Mapping = None,
        pd_uri_list: Sequence[str] = None,
    ) -> "VCRecordSearch":
        """Search for credentials."""
        return ExternalVCRecordSearch(
            self.kms,
            search_params={
                "contexts": contexts,
                "types": types,
                "schema_ids": schema_ids,
                "issuer_id": issuer_id,
                "subject_ids": subject_ids,
                "proof_types": proof_types,
                "given_id": given_id,
                "tag_query": tag_query,
                "pd_uri_list": pd_uri_list,
            },
        )
