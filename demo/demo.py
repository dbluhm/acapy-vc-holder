"""Demo script."""

import asyncio
from dataclasses import dataclass
from os import getenv
from typing import Any, Mapping, Type
from uuid import uuid4

from acapy_controller import Controller
from acapy_controller.controller import Minimal
from acapy_controller.logging import logging_to_stdout, section
from acapy_controller.protocols import (
    MinType,
    didexchange,
    jsonld_issue_credential,
    jsonld_present_proof,
)

ISSUER = getenv("ISSUER", "http://issuer:3001")
HOLDER = getenv("HOLDER", "http://holder:3001")


@dataclass
class DIDResult(Minimal):
    """Result of DID Creation."""

    result: "DID"

    @classmethod
    def deserialize(cls: Type[MinType], value: Mapping[str, Any]) -> MinType:
        """Deserialize."""
        value = dict(value)
        if result := value.get("result"):
            value["result"] = DID.deserialize(result)

        return super().deserialize(value)


@dataclass
class DID(Minimal):
    """DID Info."""

    did: str


async def main():
    """Run the demo."""
    async with Controller(ISSUER) as issuer, Controller(HOLDER) as holder:
        with section("Setup issuer DID"):
            result = await issuer.post(
                "/wallet/did/create", json={"method": "key"}, response=DIDResult
            )
            issuer_did_info = result.result

        with section("Setup External Holder Profile"):
            await holder.post("/ext/profile/setup")

        with section("Setup holder DID"):
            result = await holder.post(
                "/wallet/did/create", json={"method": "key"}, response=DIDResult
            )
            holder_did_info = result.result

        with section("Establish a connection"):
            issuer_conn, holder_conn = await didexchange(issuer, holder)

        with section("Issue an Example Cred"):
            await jsonld_issue_credential(
                issuer,
                holder,
                issuer_conn.connection_id,
                holder_conn.connection_id,
                credential={
                    "@context": [
                        "https://www.w3.org/2018/credentials/v1",
                        "https://w3id.org/citizenship/v1",
                    ],
                    "type": ["VerifiableCredential", "PermanentResident"],
                    "issuer": issuer_did_info.did,
                    "issuanceDate": "2020-01-01T19:23:24Z",
                    "credentialSubject": {
                        "type": ["PermanentResident"],
                        "id": holder_did_info.did,
                        "givenName": "Bob",
                        "familyName": "Builder",
                        "gender": "Male",
                        "birthCountry": "Bahamas",
                        "birthDate": "1958-07-17",
                    },
                },
                options={
                    "proofType": "Ed25519Signature2020",
                    "challenge": "abc",
                    "domain": "http://example.com",
                },
            )

        with section("Present the Example Cred"):
            issuer_pres, holder_pres = await jsonld_present_proof(
                issuer,
                holder,
                issuer_conn.connection_id,
                holder_conn.connection_id,
                presentation_definition={
                    "input_descriptors": [
                        {
                            "id": "citizenship_input_1",
                            "name": "EU Driver's License",
                            "schema": [
                                {
                                    "uri": "https://www.w3.org/2018/credentials#VerifiableCredential"  # noqa: E501
                                },
                                {
                                    "uri": "https://w3id.org/citizenship#PermanentResident"  # noqa: E501
                                },
                            ],
                            "constraints": {
                                "is_holder": [
                                    {
                                        "directive": "required",
                                        "field_id": [
                                            "1f44d55f-f161-4938-a659-f8026467f126"
                                        ],
                                    }
                                ],
                                "fields": [
                                    {
                                        "id": "1f44d55f-f161-4938-a659-f8026467f126",
                                        "path": ["$.credentialSubject.familyName"],
                                        "purpose": "The claim must be from one of the specified issuers",  # noqa: E501
                                        "filter": {"const": "Builder"},
                                    },
                                    {
                                        "path": ["$.credentialSubject.givenName"],
                                        "purpose": "The claim must be from one of the specified issuers",  # noqa: E501
                                    },
                                ],
                            },
                        }
                    ],
                    "id": str(uuid4()),
                    "format": {"ldp_vp": {"proof_type": ["Ed25519Signature2018"]}},
                },
                domain="test-degree",
            )


if __name__ == "__main__":
    logging_to_stdout()
    asyncio.run(main())
