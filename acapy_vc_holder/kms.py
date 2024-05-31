"""KMS Interface."""

from typing import List, Mapping, Optional, Union

from aiohttp import ClientSession
from aries_cloudagent.storage.vc_holder.vc_record import VCRecord


class MiniKMS:
    """Minimal KMS for testing."""

    OMITTED = object()

    def __init__(self, base_url: str, profile: Optional[str] = None):
        """Initialize the MiniKMS."""
        self.base_url = base_url
        self.client = ClientSession(base_url=base_url)
        self.profile = profile

    async def create_profile_if_not_exists(self, profile: str):
        """Create profile if not exists."""
        async with self.client.post("/profile", json={"name": profile}) as resp:
            if not resp.ok:
                if resp.status == 400 and "json" in resp.headers.getone("Content-Type"):
                    body = await resp.json()
                    if "already exists" in body.get("detail"):
                        pass
                    else:
                        message = f"{resp.status}: {resp.reason}; {body}"
                        raise ValueError(f"Error creating profile: {message}")
                else:
                    raise ValueError(
                        f"Error creating profile: {resp.status}: {resp.reason}"
                    )
            else:
                body = await resp.json()
                if body.get("success") is not True:
                    raise ValueError("Unknown error while creating profile")

    def with_profile(self, profile: Union[str, None, object] = OMITTED) -> "MiniKMS":
        """Create a new instance with profile."""
        if profile is not self.OMITTED:
            assert isinstance(profile, str) or profile is None
            return MiniKMS(self.base_url, profile)

        return self

    def headers(self):
        """Return headers."""
        return {"X-Profile": self.profile or "default"}

    async def store_credential(self, cred: VCRecord):
        """Store credential."""
        async with self.client.post(
            "/vc-holder/store", headers=self.headers(), json=cred.serialize()
        ) as resp:
            if not resp.ok:
                raise ValueError(f"Error storing cred: {resp.status} {resp.reason}")

            body = await resp.json()

        return body["record_id"]

    async def retrieve_credential_by_id(self, record_id: str) -> VCRecord:
        """Retrieve cred by id."""
        async with self.client.get(
            f"/vc-holder/credential/record/{record_id}", headers=self.headers()
        ) as resp:
            if not resp.ok:
                raise ValueError(
                    f"Error retrieving cred by id: {resp.status} {resp.reason}"
                )

            body = await resp.json()

        return VCRecord.deserialize(body)

    async def retrieve_credential_by_given_id(self, given_id: str) -> VCRecord:
        """Retrieve cred by id."""
        async with self.client.get(
            f"/vc-holder/credential/given/{given_id}", headers=self.headers()
        ) as resp:
            if not resp.ok:
                raise ValueError(
                    f"Error retrieving cred by given id: {resp.status} {resp.reason}"
                )

            body = await resp.json()

        return VCRecord.deserialize(body)

    async def delete_credential(self, record_id: str):
        """Delete a credential by id."""
        async with self.client.delete(
            f"/vc-holder/credential/record/{record_id}", headers=self.headers()
        ) as resp:
            if not resp.ok:
                raise ValueError(f"Error deleting cred: {resp.status} {resp.reason}")

    async def search_credentials(
        self,
        contexts: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        schema_ids: Optional[List[str]] = None,
        issuer_id: Optional[str] = None,
        subject_ids: Optional[str] = None,
        proof_types: Optional[List[str]] = None,
        given_id: Optional[str] = None,
        tag_query: Optional[Mapping] = None,
        pd_uri_list: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> List[VCRecord]:
        """Search for credentials."""
        async with self.client.post(
            "/vc-holder/credentials",
            headers=self.headers(),
            json={
                "contexts": contexts,
                "types": types,
                "schema_ids": schema_ids,
                "issuer_id": issuer_id,
                "subject_ids": subject_ids,
                "proof_types": proof_types,
                "given_id": given_id,
                "tag_query": tag_query,
                "pd_uri_list": pd_uri_list,
                "offset": offset,
                "limit": limit,
            },
        ) as resp:
            if not resp.ok:
                raise ValueError(
                    f"Error searching for credentials: {resp.status} {resp.reason}"
                )

            body = await resp.json()

        return [VCRecord.deserialize(record) for record in body["records"]]
