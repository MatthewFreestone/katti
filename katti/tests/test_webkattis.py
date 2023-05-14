import pytest
from katti import webkattis, configloader
from unittest import mock
from pathlib import Path


@pytest.fixture
def carrots_get_response():
    string = None
    path = Path('./katti/tests/carrots_get_response.html').resolve()
    with open(path, 'r') as f:
        string = f.read()
    return string


@pytest.fixture
def submission_get_response():
    string = None
    path = Path('./katti/tests/submission_get_response.html').resolve()
    with open(path, 'r') as f:
        string = f.read()
    return string


@pytest.fixture
def kattis_config():
    return configloader.KattisConfig('username', 'url', 'token')


@pytest.fixture
def problems_config():
    return configloader.ProblemsConfig()


def test_get_problem_rating(carrots_get_response, kattis_config):
    with mock.patch('katti.webkattis.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = carrots_get_response
        rating = webkattis.get_problem_rating('carrots', kattis_config)
        assert rating == 1.4
        mock_get.assert_called_with('url/problems/carrots')


def test_get_problem_rating_down(kattis_config):
    with mock.patch('katti.webkattis.requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        mock_get.return_value.text = ''
        with pytest.raises(Exception):
            rating = webkattis.get_problem_rating('carrots', kattis_config)
        mock_get.assert_called_with('url/problems/carrots')


def test_open_in_browser(kattis_config):
    with mock.patch('katti.webkattis.webbrowser.open') as mock_open:
        with mock.patch('katti.webkattis.get_problem_rating') as mock_rating:
            mock_rating.return_value = 1.4
            webkattis.show_description('carrots', kattis_config)
            mock_rating.assert_called_with('carrots', kattis_config, False)
            mock_open.assert_called_with('url/problems/carrots')


def test_check_submission_status(submission_get_response, kattis_config):
    with mock.patch('katti.webkattis.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = submission_get_response
        status = webkattis.check_submission_status('12345', kattis_config)
        assert status == 'Accepted'
        mock_get.assert_called_with('url/submissions/12345')
