"""Real PostgreSQL shape verification for the patient health hub migration."""

import os
from collections.abc import AsyncIterator
from typing import TypedDict, cast

import pytest
from sqlalchemy import DateTime, inspect
from sqlalchemy.engine import Connection

from app.config import DatabaseSettings
from app.shared.persistence import DatabaseRuntime

pytestmark = pytest.mark.postgres


class SchemaShape(TypedDict):
    account_columns: set[str]
    document_columns: set[str]
    account_constraints: set[str]
    document_constraints: set[str]
    account_indexes: set[str]
    document_indexes: set[str]
    timestamp_timezones: set[bool]


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    test_url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if test_url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=test_url))
    try:
        yield runtime
    finally:
        await runtime.dispose()


async def test_patient_hub_tables_constraints_and_indexes_exist(
    database_runtime: DatabaseRuntime,
) -> None:
    async with database_runtime.engine.connect() as connection:
        shape = await connection.run_sync(_schema_shape)

    assert shape["account_columns"] == {
        "id",
        "actor_id",
        "patient_id",
        "email_normalized",
        "email_display",
        "display_name",
        "password_hash",
        "status",
        "created_at",
        "updated_at",
    }
    assert shape["document_columns"] == {
        "id",
        "patient_id",
        "display_name",
        "mime_type",
        "byte_size",
        "object_key",
        "sha256_digest",
        "created_at",
        "deleted_at",
    }
    assert {
        "ck_patient_accounts_status_supported",
        "uq_patient_accounts_actor_id",
        "uq_patient_accounts_patient_id",
    }.issubset(shape["account_constraints"])
    assert {
        "ck_patient_documents_byte_size_positive",
        "ck_patient_documents_sha256_digest_valid",
        "uq_patient_documents_object_key",
    }.issubset(shape["document_constraints"])
    assert "ix_patient_accounts_email_normalized" in shape["account_indexes"]
    assert "ix_patient_documents_patient_id_created_at" in shape["document_indexes"]
    assert shape["timestamp_timezones"] == {True}


def _schema_shape(connection: Connection) -> SchemaShape:
    inspector = inspect(connection)
    account_columns = inspector.get_columns("patient_accounts")
    document_columns = inspector.get_columns("patient_documents")
    return {
        "account_columns": {column["name"] for column in account_columns},
        "document_columns": {column["name"] for column in document_columns},
        "account_constraints": {
            constraint["name"]
            for constraint in (
                *inspector.get_check_constraints("patient_accounts"),
                *inspector.get_unique_constraints("patient_accounts"),
            )
            if constraint["name"] is not None
        },
        "document_constraints": {
            constraint["name"]
            for constraint in (
                *inspector.get_check_constraints("patient_documents"),
                *inspector.get_unique_constraints("patient_documents"),
            )
            if constraint["name"] is not None
        },
        "account_indexes": {
            index["name"]
            for index in inspector.get_indexes("patient_accounts")
            if index["name"] is not None
        },
        "document_indexes": {
            index["name"]
            for index in inspector.get_indexes("patient_documents")
            if index["name"] is not None
        },
        "timestamp_timezones": {
            bool(cast(DateTime, column["type"]).timezone)
            for column in (*account_columns, *document_columns)
            if column["name"].endswith("_at")
        },
    }
