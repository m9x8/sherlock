import pytest
from sherlock_project import sherlock
from sherlock_interactives import Interactives
from sherlock_interactives import InteractivesSubprocessError

def test_remove_nsfw(sites_obj):
    nsfw_target: str = 'Xvideos'
    assert nsfw_target in {site.name: site.information for site in sites_obj}
    sites_obj.remove_nsfw_sites()
    assert nsfw_target not in {site.name: site.information for site in sites_obj}


# Parametrized sites should *not* include Motherless, which is acting as the control
@pytest.mark.parametrize('nsfwsites', [
    ['Xvideos'],
    ['Xvideos', 'Erome'],
])
def test_nsfw_explicit_selection(sites_obj, nsfwsites):
    for site in nsfwsites:
        assert site in {site.name: site.information for site in sites_obj}
    sites_obj.remove_nsfw_sites(do_not_remove=nsfwsites)
    for site in nsfwsites:
        assert site in {site.name: site.information for site in sites_obj}
        assert 'Motherless' not in {site.name: site.information for site in sites_obj}

def test_wildcard_username_expansion():
    assert sherlock.check_for_parameter('test{?}test') is True
    assert sherlock.check_for_parameter('test{.}test') is False
    assert sherlock.check_for_parameter('test{}test') is False
    assert sherlock.check_for_parameter('testtest') is False
    assert sherlock.check_for_parameter('test{?test') is False
    assert sherlock.check_for_parameter('test?}test') is False
    assert sherlock.multiple_usernames('test{?}test') == ["test_test" , "test-test" , "test.test"]


@pytest.mark.parametrize('cliargs', [
    '',
    '--site urghrtuight --egiotr',
    '--',
])
def test_no_usernames_provided(cliargs):
    with pytest.raises(InteractivesSubprocessError, match=r"error: the following arguments are required: USERNAMES"):
        Interactives.run_cli(cliargs)

def test_gui_textbox_url_tagging():
    from unittest.mock import MagicMock
    from sherlock_project.gui import SherlockGUI

    # Create a mock textbox that behaves like ctk.CTkTextbox
    textbox = MagicMock()

    # Store inserted parts and tags
    inserted_text = []
    tags = []

    def mock_insert(idx, text):
        inserted_text.append(text)

    def mock_index(idx):
        return str(len("".join(inserted_text)))

    def mock_tag_add(tag, start, end):
        tags.append((tag, start, end))

    textbox.insert = mock_insert
    textbox.index = mock_index
    textbox.tag_add = mock_tag_add

    gui = MagicMock()

    SherlockGUI._insert_text(gui, textbox, "Dit is een link: https://example.com en nog een https://test.org/user.")

    # Check inserted text
    full_content = "".join(inserted_text)
    assert "https://example.com" in full_content
    assert "https://test.org/user" in full_content

    # Check that tags were applied on the expected link parts
    assert len(tags) >= 2
    assert tags[0][0] == "link"
    assert tags[1][0] == "link"
