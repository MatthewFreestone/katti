import pytest
from katti import webkattis
from unittest import mock

def test_webbrowser():
    with mock.patch('webbrowser.open') as mock_open:
        webkattis.webbrowser()
        mock_open.assert_called_with('https://open.kattis.com/problems/')