<!-- This README should be a mini version at all times for use on pypi -->

<p align=center>
  <br>
  <a href="https://sherlock-project.github.io/" target="_blank"><img src="https://www.kali.org/tools/sherlock/images/sherlock-logo.svg" width="25%"/></a>
  <br>
  <strong><span>Hunt down social media accounts by username across <a href="https://github.com/sherlock-project/sherlock/blob/master/sites.md">400+ social networks</a></span></strong>
  <br><br>
  <span>Additional documentation can be found at our <a href="https://github.com/sherlock-project/sherlock/">GitHub repository</a></span>
  <br>
</p>

## GUI & Phone OSINT Features

Sherlock includes a beautiful Graphical User Interface and a Phone Number OSINT lookup tool:
- **Graphical Interface**: Run `sherlock --gui` to launch a fully professional graphical interface built with CustomTkinter.
- **Phone Number OSINT**: Search for phone numbers, validate formats, retrieve carrier/geocoding metadata, and crawl the web for public mentions and social media accounts.
- **Advanced Export options**: Generate report exports with scanning metadata in TXT, Microsoft Word (.docx), or custom styled PDFs.

## Usage

```console
$ sherlock --help
usage: sherlock [-h] [--version] [--verbose] [--folderoutput FOLDEROUTPUT]
                [--output OUTPUT] [--tor] [--unique-tor] [--csv] [--xlsx]
                [--site SITE_NAME] [--proxy PROXY_URL] [--json JSON_FILE]
                [--timeout TIMEOUT] [--print-all] [--print-found] [--no-color]
                [--browse] [--local] [--nsfw]
                USERNAMES [USERNAMES ...]
```

To search for only one user:
```bash
$ sherlock user123
```

To search for more than one user:
```bash
$ sherlock user1 user2 user3
```
<br>

___

<br>
<p align="center">
<img width="70%" height="70%" src="https://user-images.githubusercontent.com/27065646/219638267-a5e11090-aa6e-4e77-87f7-0e95f6ad5978.png"/>
</a>
</p>
