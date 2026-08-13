import re

with open('sherlock_project/phone_search.py', 'r') as f:
    content = f.read()

# 1. Update phone dorks
old_phone_dorks = """        dorks = {
            "Lek- & Paste-sites": f"(site:pastebin.com OR site:paste.org OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:paste2.org OR site:ghostbin.co OR site:controlc.com OR site:pastelink.net OR site:rentry.co) ({terms_or})",
            "Documenten & Resumes": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv OR filetype:tsv) ({terms_or})",
            "Professionele Netwerken": f"(site:linkedin.com/in OR site:linkedin.com/pub OR site:xing.com OR site:rocketreach.co OR site:apollo.io OR site:zoominfo.com OR site:lusha.com OR site:signalhire.com OR site:contactout.com) ({terms_or})",
            "Chat- & Messenger-groepen": f"(site:t.me OR site:chat.whatsapp.com OR site:discord.gg OR site:signal.group OR site:line.me OR site:viber.com) ({terms_or})",
            "Adresboeken & Spam-registries": f"(site:tellows.nl OR site:tellows.com OR site:sync.me OR site:truecaller.com OR site:whocalledme.com OR site:wieheeftgebeld.nl OR site:telefoonboek.nl OR site:openingstijden.nl OR site:zoeknummer.nl OR site:wieheeftmijgebeld.nl OR site:spamcalls.net) ({terms_or})"
        }"""

new_phone_dorks = """        dorks = {
            "Lek- & Paste-sites": f"(site:pastebin.com OR site:paste.org OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:paste2.org OR site:ghostbin.co OR site:controlc.com OR site:pastelink.net OR site:rentry.co) ({terms_or})",
            "Documenten & Resumes": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv OR filetype:tsv) ({terms_or})",
            "Professionele Netwerken": f"(site:linkedin.com/in OR site:linkedin.com/pub OR site:xing.com OR site:rocketreach.co OR site:apollo.io OR site:zoominfo.com OR site:lusha.com OR site:signalhire.com OR site:contactout.com) ({terms_or})",
            "Chat- & Messenger-groepen": f"(site:t.me OR site:chat.whatsapp.com OR site:discord.gg OR site:signal.group OR site:line.me OR site:viber.com) ({terms_or})",
            "Adresboeken & Spam-registries": f"(site:tellows.nl OR site:tellows.com OR site:sync.me OR site:truecaller.com OR site:whocalledme.com OR site:wieheeftgebeld.nl OR site:telefoonboek.nl OR site:openingstijden.nl OR site:zoeknummer.nl OR site:wieheeftmijgebeld.nl OR site:spamcalls.net) ({terms_or})",
            "Marktplaatsen & Advertenties": f"(site:marktplaats.nl OR site:tweakers.net OR site:2dehands.be OR site:craigslist.org OR site:ebay.com) ({terms_or})",
            "Forums & Blogs": f"(site:forum.fok.nl OR site:gathering.tweakers.net OR site:kassa.bnnvara.nl OR site:radar.avrotros.nl) ({terms_or})",
            "Overheid & Openbare Documenten": f"(site:overheid.nl OR site:rijksoverheid.nl OR site:officielebekendmakingen.nl OR site:rechtspraak.nl) ({terms_or})"
        }"""
content = content.replace(old_phone_dorks, new_phone_dorks)


# 2. Update username dorks
old_username_dorks = """        dorks = {
            "Lek- & Paste-sites": f"(site:pastebin.com OR site:paste.org OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:paste2.org OR site:ghostbin.co OR site:controlc.com OR site:pastelink.net OR site:rentry.co) {escaped_username}",
            "Documenten & Resumes": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv OR filetype:tsv) {escaped_username}",
            "Professionele Netwerken": f"(site:linkedin.com/in OR site:linkedin.com/pub OR site:xing.com OR site:rocketreach.co OR site:apollo.io OR site:zoominfo.com OR site:lusha.com OR site:signalhire.com OR site:contactout.com) {escaped_username}",
            "Chat- & Messenger-groepen": f"(site:t.me OR site:chat.whatsapp.com OR site:discord.gg OR site:signal.group OR site:line.me OR site:viber.com) {escaped_username}",
            "Adresboeken & Spam-registries": f"(site:tellows.nl OR site:tellows.com OR site:sync.me OR site:truecaller.com OR site:whocalledme.com OR site:wieheeftgebeld.nl OR site:telefoonboek.nl OR site:openingstijden.nl OR site:zoeknummer.nl OR site:wieheeftmijgebeld.nl OR site:spamcalls.net) {escaped_username}"
        }"""

new_username_dorks = """        dorks = {
            "Lek- & Paste-sites": f"(site:pastebin.com OR site:paste.org OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:paste2.org OR site:ghostbin.co OR site:controlc.com OR site:pastelink.net OR site:rentry.co) {escaped_username}",
            "Documenten & Resumes": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv OR filetype:tsv) {escaped_username}",
            "Professionele Netwerken": f"(site:linkedin.com/in OR site:linkedin.com/pub OR site:xing.com OR site:rocketreach.co OR site:apollo.io OR site:zoominfo.com OR site:lusha.com OR site:signalhire.com OR site:contactout.com) {escaped_username}",
            "Chat- & Messenger-groepen": f"(site:t.me OR site:chat.whatsapp.com OR site:discord.gg OR site:signal.group OR site:line.me OR site:viber.com) {escaped_username}",
            "Adresboeken & Spam-registries": f"(site:tellows.nl OR site:tellows.com OR site:sync.me OR site:truecaller.com OR site:whocalledme.com OR site:wieheeftgebeld.nl OR site:telefoonboek.nl OR site:openingstijden.nl OR site:zoeknummer.nl OR site:wieheeftmijgebeld.nl OR site:spamcalls.net) {escaped_username}",
            "Tech & Developer Platformen": f"(site:stackoverflow.com OR site:hackernews.com OR site:dev.to OR site:hashnode.com OR site:medium.com OR site:gitlab.com OR site:bitbucket.org OR site:sourceforge.net) {escaped_username}",
            "Gaming & Entertainment": f"(site:steamcommunity.com OR site:twitch.tv OR site:xbox.com OR site:playstation.com OR site:ign.com OR site:roblox.com) {escaped_username}",
            "Forums & Communities": f"(site:reddit.com/user OR site:quora.com/profile OR site:forum.fok.nl OR site:gathering.tweakers.net OR site:4chan.org) {escaped_username}",
            "Dating & Lifestyle": f"(site:tinder.com OR site:badoo.com OR site:okcupid.com OR site:pof.com OR site:last.fm OR site:myanimelist.net) {escaped_username}",
            "Crypto & Darkweb Links": f"(site:bitcointalk.org OR site:etherscan.io/address OR site:opensea.io) {escaped_username}"
        }"""

content = content.replace(old_username_dorks, new_username_dorks)

with open('sherlock_project/phone_search.py', 'w') as f:
    f.write(content)
