"""
Tests for db.py - SQLite deduplication logic.
"""
import sqlite3
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Use in-memory DB for tests by patching DB_PATH
import config
config.DB_PATH = ":memory:"

from db import get_conn, job_id, is_new, mark_seen


@pytest.fixture
def conn():
    c = get_conn()
    yield c
    c.close()


class TestJobId:
    def test_deterministic(self):
        assert job_id("PostDoc in CS", "http://example.com/1") == job_id("PostDoc in CS", "http://example.com/1")

    def test_different_title(self):
        assert job_id("PostDoc in CS", "http://example.com/1") != job_id("PostDoc in Bio", "http://example.com/1")

    def test_different_url(self):
        assert job_id("PostDoc in CS", "http://example.com/1") != job_id("PostDoc in CS", "http://example.com/2")

    def test_returns_hex_string(self):
        result = job_id("title", "url")
        assert isinstance(result, str)
        assert len(result) == 32  # MD5 hex length


class TestIsNew:
    def test_new_job_is_new(self, conn):
        assert is_new(conn, "New Postdoc", "http://example.com/new") is True

    def test_seen_job_is_not_new(self, conn):
        mark_seen(conn, "Seen Postdoc", "http://example.com/seen", "TestSource")
        assert is_new(conn, "Seen Postdoc", "http://example.com/seen") is False

    def test_different_title_same_url_is_new(self, conn):
        mark_seen(conn, "PostDoc A", "http://example.com/job1", "src")
        assert is_new(conn, "PostDoc B", "http://example.com/job1") is True

    def test_same_title_different_url_is_new(self, conn):
        mark_seen(conn, "PostDoc A", "http://example.com/job1", "src")
        assert is_new(conn, "PostDoc A", "http://example.com/job2") is True


class TestMarkSeen:
    def test_mark_seen_inserts_record(self, conn):
        mark_seen(conn, "PostDoc X", "http://example.com/x", "SiteX")
        row = conn.execute("SELECT title, url, source FROM seen_jobs WHERE title='PostDoc X'").fetchone()
        assert row is not None
        assert row[0] == "PostDoc X"
        assert row[1] == "http://example.com/x"
        assert row[2] == "SiteX"

    def test_mark_seen_idempotent(self, conn):
        """Marking same job twice should not raise an error."""
        mark_seen(conn, "PostDoc Y", "http://example.com/y", "SiteY")
        mark_seen(conn, "PostDoc Y", "http://example.com/y", "SiteY")
        count = conn.execute("SELECT COUNT(*) FROM seen_jobs WHERE title='PostDoc Y'").fetchone()[0]
        assert count == 1
