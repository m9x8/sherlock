import os
import json
from unittest.mock import MagicMock, patch
import pytest
from sherlock_project.gui import (
    TRANSLATIONS,
    load_settings,
    save_settings,
    SherlockGUI,
    SETTINGS_FILE
)

def test_translation_keys_match():
    # Ensure Dutch and English translation tables have the exact same set of keys
    assert set(TRANSLATIONS["nl"].keys()) == set(TRANSLATIONS["en"].keys())

def test_load_save_settings(tmp_path):
    # Test setting persistence
    temp_settings_file = tmp_path / "settings.json"
    with patch("sherlock_project.gui.SETTINGS_FILE", str(temp_settings_file)):
        # Default when file doesn't exist
        settings = load_settings()
        assert settings == {"language": "nl", "shodan_api_key": ""}

        # Save some settings
        save_settings({"language": "en", "shodan_api_key": "dummy_key", "other_option": True})

        # Load and verify
        settings_loaded = load_settings()
        assert settings_loaded["language"] == "en"
        assert settings_loaded["other_option"] is True

def test_get_text_with_mock_instance():
    # Test get_text on a mock instance of SherlockGUI to avoid Display/TclError in headless environments
    gui = MagicMock()
    gui.language_var = MagicMock()

    # Test Dutch
    gui.language_var.get.return_value = "nl"
    assert SherlockGUI.get_text(gui, "tab_username") == "Gebruikersnaam Zoeken"
    assert SherlockGUI.get_text(gui, "settings_title") == "Applicatie Instellingen"

    # Test English
    gui.language_var.get.return_value = "en"
    assert SherlockGUI.get_text(gui, "tab_username") == "Username Search"
    assert SherlockGUI.get_text(gui, "settings_title") == "Application Settings"

@patch("subprocess.run")
def test_run_check_updates_up_to_date(mock_run):
    gui = MagicMock()
    gui.language_var = MagicMock()
    gui.language_var.get.return_value = "nl"

    # Mock subprocess to simulate lagging_count = 0 (up to date)
    mock_git_check = MagicMock()
    mock_git_check.returncode = 0
    mock_fetch = MagicMock()
    mock_rev_list = MagicMock()
    mock_rev_list.stdout = "0\n"
    mock_run.side_effect = [mock_git_check, mock_fetch, mock_rev_list]

    # Run check
    SherlockGUI._run_check_updates(gui)

    # Verify that up-to-date callback was scheduled via after()
    gui.after.assert_called_once()
    # Execute the lambda scheduled in after
    callback = gui.after.call_args[0][1]
    callback()

    # Ensure up-to-date action is triggered
    gui._update_up_to_date_action.assert_called_once()

@patch("subprocess.run")
def test_run_check_updates_available(mock_run):
    gui = MagicMock()
    gui.language_var = MagicMock()
    gui.language_var.get.return_value = "nl"

    # Mock subprocess to simulate lagging_count = 5 (update available)
    mock_git_check = MagicMock()
    mock_git_check.returncode = 0
    mock_fetch = MagicMock()
    mock_rev_list = MagicMock()
    mock_rev_list.stdout = "5\n"
    mock_run.side_effect = [mock_git_check, mock_fetch, mock_rev_list]

    # Run check
    SherlockGUI._run_check_updates(gui)

    # Verify that callback was scheduled via after()
    gui.after.assert_called_once()
    # Execute the lambda scheduled in after
    callback = gui.after.call_args[0][1]
    callback()

    # Ensure available action is triggered
    gui._update_available_action.assert_called_once()
