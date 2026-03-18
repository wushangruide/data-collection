"""
Tests for notifier.py - Server酱 WeChat push logic.
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config

from notifier import push_jobs, _print_jobs, _send


SAMPLE_JOBS = [
    {"title": "Postdoc in ML", "url": "http://example.com/1", "location": "MIT, USA", "source": "TestSite"},
    {"title": "Postdoc in Psychology", "url": "http://example.com/2", "location": "", "source": "TestSite2"},
]


class TestPushJobs:
    def setup_method(self):
        config.SERVERCHAN_KEY = "YOUR_SERVERCHAN_KEY_HERE"

    def teardown_method(self):
        config.SERVERCHAN_KEY = "YOUR_SERVERCHAN_KEY_HERE"

    def test_empty_jobs_no_push(self):
        """push_jobs with empty list should not call _send."""
        with patch("notifier._send") as mock_send:
            push_jobs([])
            mock_send.assert_not_called()

    def test_unconfigured_key_prints_instead(self, capsys):
        """When key is not configured, fallback to _print_jobs."""
        with patch("notifier._send") as mock_send:
            push_jobs(SAMPLE_JOBS)
            mock_send.assert_not_called()
        captured = capsys.readouterr()
        assert "Postdoc in ML" in captured.out

    def test_configured_key_calls_send(self):
        """When key is configured, _send should be called."""
        config.SERVERCHAN_KEY = "SCT_REAL_KEY_123"
        with patch("notifier._send") as mock_send:
            push_jobs(SAMPLE_JOBS)
            mock_send.assert_called_once()
            title_arg = mock_send.call_args[0][0]
            assert "2" in title_arg  # "2 条新职位"

    def test_push_message_contains_job_titles(self):
        config.SERVERCHAN_KEY = "SCT_REAL_KEY_123"
        with patch("notifier._send") as mock_send:
            push_jobs(SAMPLE_JOBS)
            content_arg = mock_send.call_args[0][1]
            assert "Postdoc in ML" in content_arg
            assert "Postdoc in Psychology" in content_arg

    def test_push_message_contains_urls(self):
        config.SERVERCHAN_KEY = "SCT_REAL_KEY_123"
        with patch("notifier._send") as mock_send:
            push_jobs(SAMPLE_JOBS)
            content_arg = mock_send.call_args[0][1]
            assert "http://example.com/1" in content_arg


class TestSend:
    def setup_method(self):
        config.SERVERCHAN_KEY = "SCT_TEST_KEY"

    def teardown_method(self):
        config.SERVERCHAN_KEY = "YOUR_SERVERCHAN_KEY_HERE"

    def test_send_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 0, "message": "ok"}
        mock_resp.raise_for_status = MagicMock()

        with patch("notifier.requests.post", return_value=mock_resp) as mock_post:
            _send("Test Title", "Test Content")
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args
            assert "SCT_TEST_KEY.send" in call_kwargs[0][0]

    def test_send_api_error_logged(self, caplog):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 999, "message": "error"}
        mock_resp.raise_for_status = MagicMock()

        with patch("notifier.requests.post", return_value=mock_resp):
            import logging
            with caplog.at_level(logging.ERROR, logger="notifier"):
                _send("Title", "Content")
            assert "推送失败" in caplog.text

    def test_send_network_exception_logged(self, caplog):
        with patch("notifier.requests.post", side_effect=Exception("network error")):
            import logging
            with caplog.at_level(logging.ERROR, logger="notifier"):
                _send("Title", "Content")
            assert "推送异常" in caplog.text


class TestPrintJobs:
    def test_print_jobs_output(self, capsys):
        _print_jobs(SAMPLE_JOBS)
        captured = capsys.readouterr()
        assert "Postdoc in ML" in captured.out
        assert "http://example.com/1" in captured.out
        assert "MIT, USA" in captured.out
        assert "Postdoc in Psychology" in captured.out
