with open('sherlock_project/dox_search.py', 'r') as f:
    content = f.read()

old_dox = """        results = {
            "Gevonden Adressen & Kadaster": [],
            "Relaties, Familie & Connecties": [],
            "Gekoppelde Bedrijven & Directies": [],
            "Lekken, Gegevensbreuken & Pastes": [],
            "Social Media & Online Voetafdruk": []
        }

        # Calculate steps: we have queries for each field if filled
        queries_to_run = []

        # Build composite target details
        target_indicators = []
        if name:
            target_indicators.append(f'"{name}"')
        if city:
            target_indicators.append(f'"{city}"')
        if phone:
            target_indicators.append(f'"{phone}"')
        if email:
            target_indicators.append(f'"{email}"')
        if username:
            target_indicators.append(f'"{username}"')

        if not target_indicators:
            return results

        composite_or = " OR ".join(target_indicators)

        # 1. Address, Physical Locations & Kadaster
        q1 = f"(site:kadaster.nl OR site:overheid.nl OR site:infobel.com OR site:telefoonboek.nl OR site:drimble.nl OR site:openadres.nl) ({composite_or})"
        queries_to_run.append(("Gevonden Adressen & Kadaster", q1))

        # 2. Family, Relatives & Associations
        q2 = f"(site:stamboomzoeker.nl OR site:genealogieonline.nl OR site:facebook.com OR site:linkedin.com/in OR site:familieberichten.nl) ({composite_or}) (\\"familie\\" OR \\"relatie\\" OR \\"gehuwd\\" OR \\"partner\\" OR \\"zoon\\" OR \\"dochter\\")"
        queries_to_run.append(("Relaties, Familie & Connecties", q2))

        # 3. Companies & Directorships
        q3 = f"(site:kvk.nl OR site:opencorporates.com OR site:companyinfo.nl OR site:drimble.nl OR site:find-and-update.company-information.service.gov.uk) ({composite_or})"
        queries_to_run.append(("Gekoppelde Bedrijven & Directies", q3))

        # 4. Leaks & Databases
        q4 = f"(site:pastebin.com OR site:paste.org OR site:gitter.im OR site:github.com OR site:gitlab.com OR site:dehashed.com OR site:leak-lookup.com) ({composite_or})"
        queries_to_run.append(("Lekken, Gegevensbreuken & Pastes", q4))

        # 5. Social Presence & Footprint
        q5 = f"(site:instagram.com OR site:facebook.com OR site:twitter.com OR site:x.com OR site:pinterest.com OR site:tiktok.com OR site:youtube.com OR site:reddit.com/user) ({composite_or})"
        queries_to_run.append(("Social Media & Online Voetafdruk", q5))"""

new_dox = """        results = {
            "Gevonden Adressen & Kadaster": [],
            "Relaties, Familie & Connecties": [],
            "Gekoppelde Bedrijven & Directies": [],
            "Lekken, Gegevensbreuken & Pastes": [],
            "Social Media & Online Voetafdruk": [],
            "Juridisch, Insolventies & Overheid": [],
            "Voertuigen & Transport": [],
            "Crypto, Darkweb & P2P": [],
            "Archieven & Historische Data": [],
            "Documenten & Verborgen Bestanden": []
        }

        # Calculate steps: we have queries for each field if filled
        queries_to_run = []

        # Build composite target details
        target_indicators = []
        if name:
            target_indicators.append(f'"{name}"')
        if city:
            target_indicators.append(f'"{city}"')
        if phone:
            target_indicators.append(f'"{phone}"')
        if email:
            target_indicators.append(f'"{email}"')
        if username:
            target_indicators.append(f'"{username}"')

        if not target_indicators:
            return results

        composite_or = " OR ".join(target_indicators)

        # 1. Address, Physical Locations & Kadaster
        q1 = f"(site:kadaster.nl OR site:overheid.nl OR site:infobel.com OR site:telefoonboek.nl OR site:drimble.nl OR site:openadres.nl) ({composite_or})"
        queries_to_run.append(("Gevonden Adressen & Kadaster", q1))

        # 2. Family, Relatives & Associations
        q2 = f"(site:stamboomzoeker.nl OR site:genealogieonline.nl OR site:facebook.com OR site:linkedin.com/in OR site:familieberichten.nl) ({composite_or}) (\\"familie\\" OR \\"relatie\\" OR \\"gehuwd\\" OR \\"partner\\" OR \\"zoon\\" OR \\"dochter\\")"
        queries_to_run.append(("Relaties, Familie & Connecties", q2))

        # 3. Companies & Directorships
        q3 = f"(site:kvk.nl OR site:opencorporates.com OR site:companyinfo.nl OR site:drimble.nl OR site:find-and-update.company-information.service.gov.uk) ({composite_or})"
        queries_to_run.append(("Gekoppelde Bedrijven & Directies", q3))

        # 4. Leaks & Databases
        q4 = f"(site:pastebin.com OR site:paste.org OR site:gitter.im OR site:github.com OR site:gitlab.com OR site:dehashed.com OR site:leak-lookup.com) ({composite_or})"
        queries_to_run.append(("Lekken, Gegevensbreuken & Pastes", q4))

        # 5. Social Presence & Footprint
        q5 = f"(site:instagram.com OR site:facebook.com OR site:twitter.com OR site:x.com OR site:pinterest.com OR site:tiktok.com OR site:youtube.com OR site:reddit.com/user) ({composite_or})"
        queries_to_run.append(("Social Media & Online Voetafdruk", q5))

        # 6. Legal, Insolvencies & Gov
        q6 = f"(site:rechtspraak.nl OR site:officielebekendmakingen.nl OR site:faillissementsdossier.nl OR site:interpol.int) ({composite_or})"
        queries_to_run.append(("Juridisch, Insolventies & Overheid", q6))

        # 7. Vehicles & Transport
        q7 = f"(site:rdw.nl OR site:kentekencheck.nl OR site:autoweek.nl OR site:flitsmeister.nl/gebruiker OR site:uber.com) ({composite_or})"
        queries_to_run.append(("Voertuigen & Transport", q7))

        # 8. Crypto, Darkweb & P2P
        q8 = f"(site:bitcointalk.org OR site:etherscan.io OR site:blockchain.com OR site:localbitcoins.com OR site:opensea.io) ({composite_or})"
        queries_to_run.append(("Crypto, Darkweb & P2P", q8))

        # 9. Archives & Historical Data
        q9 = f"(site:archive.org OR site:delpher.nl OR site:waybackmachine.org) ({composite_or})"
        queries_to_run.append(("Archieven & Historische Data", q9))

        # 10. Documents & Hidden Files
        q10 = f"(filetype:pdf OR filetype:xls OR filetype:xlsx OR filetype:doc OR filetype:docx OR filetype:txt OR filetype:csv) ({composite_or}) (vertrouwelijk OR confidential OR dossier OR rapport OR geheim)"
        queries_to_run.append(("Documenten & Verborgen Bestanden", q10))"""

content = content.replace(old_dox, new_dox)

with open('sherlock_project/dox_search.py', 'w') as f:
    f.write(content)
