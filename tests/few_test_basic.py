import sherlock_project

#from sherlock.sites import SitesInformation
#local_manifest = data_file_path=os.path.join(os.path.dirname(__file__), "../sherlock/resources/data.json")

from sherlock_interactives import Interactives

def test_username_via_message():
    assert "Sherlock v" in Interactives.run_cli("--version")
