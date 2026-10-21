# mihirajmera.github.io

Portfolio and writing of Mihir Ajmera: https://mihirajmera.github.io/

Jekyll on GitHub Pages; there's no build step to run locally. See [WRITING.md](WRITING.md) for the publishing workflow and topic backlog.

| To... | Edit |
|---|---|
| Publish a note or essay | write `_drafts/<slug>.md`, then `python tools/publish.py _drafts/<slug>.md` |
| Add a headline number to the proof wall | `_data/proof.yml` (every number needs a source link) |
| Log research, releases or fixes | `_data/ledger.yml` (blog posts appear in the ledger automatically) |
| Add or change a project | `_data/projects.yml` (`flagship: true` adds it to the live status card) |
| Connect Substack, Medium, etc. | fill in the `url` in `_data/profiles.yml` |

The home page's status card reads live data from the public GitHub, PyPI and OpenSSF Scorecard APIs in the browser. Every page has Open Graph tags, `/feed.xml` is the RSS feed, and the light/dark switch remembers each visitor's choice. `portfolio.html` and `/projects/` redirect so older links keep working.
