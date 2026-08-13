with open('sherlock_project/person_search.py', 'r') as f:
    content = f.read()

old_person_dorks = """        dorks = {
            "Sociale Media & Profielen": f"(site:linkedin.com/in OR site:facebook.com OR site:instagram.com OR site:twitter.com OR site:x.com OR site:pinterest.com OR site:linktr.ee OR site:tiktok.com OR site:youtube.com OR site:github.com OR site:gravatar.com OR site:xing.com OR site:reddit.com/user OR site:flickr.com OR site:vimeo.com OR site:soundcloud.com OR site:behance.net) {escaped_name}{extra_query}",
            "CV's & Resumes (Documenten)": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv) (resume OR cv OR \\"curriculum vitae\\" OR portfolio OR bio OR biography OR \\"personal profile\\") {escaped_name}{extra_query}",
            "Nieuws, Artikelen & Pers": f"(site:nieuws.nl OR site:telegraaf.nl OR site:nu.nl OR site:nos.nl OR site:ad.nl OR site:medium.com OR site:linkedin.com/pulse OR site:reuters.com OR site:bloomberg.com OR site:nytimes.com OR site:theguardian.com OR site:ft.com OR site:volkskrant.nl OR site:nrc.nl) {escaped_name}{extra_query}",
            "Bedrijfsconnecties & Directies": f"(site:kvk.nl OR site:opencorporates.com OR site:companyinfo.nl OR site:drimble.nl OR site:find-and-update.company-information.service.gov.uk OR site:croco.nl OR site:staatsbladmonitor.be OR site:unternehmensregister.de OR site:apollo.io OR site:zoominfo.com OR site:rocketreach.co) {escaped_name}{extra_query}",
            "Lekken, Paste & Code Gidsen": f"(site:pastebin.com OR site:paste.org OR site:paste.fo OR site:rentry.co OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:controlc.com OR site:ghostbin.co OR site:pastelink.net OR site:leak-lookup.com OR site:dehashed.com) {escaped_name}{extra_query}"
        }"""

new_person_dorks = """        dorks = {
            "Sociale Media & Profielen": f"(site:linkedin.com/in OR site:facebook.com OR site:instagram.com OR site:twitter.com OR site:x.com OR site:pinterest.com OR site:linktr.ee OR site:tiktok.com OR site:youtube.com OR site:github.com OR site:gravatar.com OR site:xing.com OR site:reddit.com/user OR site:flickr.com OR site:vimeo.com OR site:soundcloud.com OR site:behance.net) {escaped_name}{extra_query}",
            "CV's & Resumes (Documenten)": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv) (resume OR cv OR \\"curriculum vitae\\" OR portfolio OR bio OR biography OR \\"personal profile\\") {escaped_name}{extra_query}",
            "Nieuws, Artikelen & Pers": f"(site:nieuws.nl OR site:telegraaf.nl OR site:nu.nl OR site:nos.nl OR site:ad.nl OR site:medium.com OR site:linkedin.com/pulse OR site:reuters.com OR site:bloomberg.com OR site:nytimes.com OR site:theguardian.com OR site:ft.com OR site:volkskrant.nl OR site:nrc.nl) {escaped_name}{extra_query}",
            "Bedrijfsconnecties & Directies": f"(site:kvk.nl OR site:opencorporates.com OR site:companyinfo.nl OR site:drimble.nl OR site:find-and-update.company-information.service.gov.uk OR site:croco.nl OR site:staatsbladmonitor.be OR site:unternehmensregister.de OR site:apollo.io OR site:zoominfo.com OR site:rocketreach.co) {escaped_name}{extra_query}",
            "Lekken, Paste & Code Gidsen": f"(site:pastebin.com OR site:paste.org OR site:paste.fo OR site:rentry.co OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:controlc.com OR site:ghostbin.co OR site:pastelink.net OR site:leak-lookup.com OR site:dehashed.com) {escaped_name}{extra_query}",
            "Academisch & Onderzoek": f"(site:researchgate.net OR site:academia.edu OR site:scholar.google.com OR site:orcid.org OR site:pubmed.ncbi.nlm.nih.gov OR site:ssrn.com) {escaped_name}{extra_query}",
            "Sport & Hobby's": f"(site:strava.com/athletes OR site:runkeeper.com OR site:chess.com/member OR site:lichess.org/@) {escaped_name}{extra_query}",
            "Genealogie & Publieke Registers": f"(site:wiewaswie.nl OR site:stamboomzoeker.nl OR site:genealogieonline.nl OR site:myheritage.nl OR site:familysearch.org) {escaped_name}{extra_query}",
            "Overheid & Juridisch": f"(site:rechtspraak.nl OR site:officielebekendmakingen.nl OR site:faillissementsdossier.nl OR site:insolventies.rechtspraak.nl) {escaped_name}{extra_query}"
        }"""

content = content.replace(old_person_dorks, new_person_dorks)

with open('sherlock_project/person_search.py', 'w') as f:
    f.write(content)
