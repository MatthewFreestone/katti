import pytest
from katti import configloader
import json


@pytest.fixture
def sample_problem_config():
    return {'carrots': 1.4, '10kindsofpeople': 4.0}


@pytest.fixture
def default_user_config():
    return {
        "ids_last_updated": "2023-02-19 15:20:56",
        "ratings_update_period": 72
    }


@pytest.fixture
def example_user_config():
    return {
        "preferred_language": "Python",
        "ids_last_updated": "2023-02-19 15:20:56",
        "ratings_update_period": 24
    }


def test_load_user_config_missing(tmp_path, default_user_config):
    '''Config File completely missing'''
    path = tmp_path / "config.json"
    user_conf = configloader.load_user_config(path)
    for key in default_user_config.keys():
        if key == "ids_last_updated":
            continue
        assert default_user_config[key] == user_conf[key]
    assert "ids_last_updated" in user_conf


def test_load_user_config_empty(tmp_path, default_user_config):
    '''Config is exists, but is empty'''
    path = tmp_path / "config.json"
    path.touch()
    with open(path, "w") as f:
        f.write("{}")
    user_conf = configloader.load_user_config(path)
    for key in default_user_config.keys():
        if key == "ids_last_updated":
            continue
        assert default_user_config[key] == user_conf[key]
    assert "ids_last_updated" in user_conf


def test_load_user_config_existing(tmp_path, example_user_config):
    '''Config File exists and is not empty'''
    path = tmp_path / "config.json"
    path.touch()
    with open(path, "w") as f:
        json.dump(example_user_config, f)

    user_conf = configloader.load_user_config(path)
    for key in example_user_config.keys():
        assert example_user_config[key] == user_conf[key]


def test_load_problems_config_missing(tmp_path):
    '''Config File completely missing'''
    path = tmp_path / "config.json"
    user_conf = configloader.load_problems_config(path)
    assert user_conf == {}


def test_load_problems_config_empty(tmp_path):
    '''Config is exists, but is empty'''
    path = tmp_path / "config.json"
    path.touch()
    with open(path, "w") as f:
        f.write("{}")
    user_conf = configloader.load_problems_config(path)
    assert user_conf == {}


def test_load_problems_config_existing(tmp_path, sample_problem_config):
    '''Config File exists and is not empty'''
    path = tmp_path / "config.json"
    path.touch()
    with open(path, "w") as f:
        json.dump(sample_problem_config, f)

    user_conf = configloader.load_problems_config(path)
    for key in sample_problem_config.keys():
        assert sample_problem_config[key] == user_conf[key]
