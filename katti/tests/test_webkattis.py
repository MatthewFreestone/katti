import pytest
from katti import webkattis
from unittest import mock
from pathlib import Path

@pytest.fixture
def carrots_get_response():
    string = None
    path = Path('./katti/tests/carrots_get_response.html').resolve()
    with open(path, 'r') as f:
        string = f.read()
    return string
    

def test_get_problem_rating(carrots_get_response):
    with mock.patch('katti.webkattis.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = carrots_get_response
        rating = webkattis.get_problem_rating('carrots')
        assert rating == 1.4
        mock_get.assert_called_with('https://open.kattis.com/problems/carrots')

def test_get_problem_rating_down(carrots_get_response):
    with mock.patch('katti.webkattis.requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        mock_get.return_value.text = ''
        with pytest.raises(Exception):
            rating = webkattis.get_problem_rating('carrots') 
        assert rating == None
        mock_get.assert_called_with('https://open.kattis.com/problems/carrots')

        