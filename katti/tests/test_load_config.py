import unittest.mock as mock
import pytest
from katti import configloader
from pathlib import Path

@pytest.fixture
def sample_problem_config():
    return {'carrots': 1.4, '10kindsofpeople': 4.0}

@pytest.fixture
def default_user_config():
    return {
        "solved": [],
        "history": [],
        "history_size": 100,
        "ids_last_updated": "2023-02-19 15:20:56.758676",
        "ratings_update_period": 72
    }

def test_load_user_config(default_user_config):
    '''Config is empty'''
    mock_open = mock.mock_open()
    mock_os_path = mock.MagicMock()
    mock_os_path.exists.side_effect = lambda x: False if x == path else None
    path = Path("./tmp").resolve()
    with mock.patch('__main__.open', mock_open):
        with mock.patch('os.path', mock_os_path):
            player_conf = configloader.load_user_config(path)
    # should check that path exists
    mock_os_path.exists.assert_called_once_with(path)

    #when if finds that it doesnt, should return 
    for key in default_user_config.keys():
        if key == "ids_last_updated":
            continue
        assert default_user_config[key] == player_conf[key]
    assert "ids_last_updated" in player_conf
    
