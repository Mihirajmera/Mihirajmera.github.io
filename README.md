# mihirajmera.github.io

Portfolio and writing of Mihir Ajmera: https://mihirajmera.github.io/

Built with Jekyll on GitHub Pages; no build step to run locally.

| To... | Edit |
|---|---|
| Add a blog post | `_posts/YYYY-MM-DD-slug.md` with `title`, `description`, `tags` (and optional `image`, `canonical_url`) |
| Add or change a project | `_data/projects.yml` (`flagship: true` puts it on the home page) |
| Add a case study | `_data/case_studies.yml` |
| Connect Substack, Medium, etc. | fill in the `url` in `_data/profiles.yml`; it appears in the footer and on `/links/` |

Cross-posting: Medium's "Import a story" takes a post URL and sets the canonical link back here; Substack's importer can pull posts from this site. `/feed.xml` (RSS) works in any reader, and every page carries Open Graph tags for LinkedIn previews. `portfolio.html` redirects to the home page so older links keep working.
