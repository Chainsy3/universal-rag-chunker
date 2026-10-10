# Project website

[中文](website.cn.md) · [English](website.en.md)

Static website sources are in `site/`, without build-tool dependencies, third-party fonts or analytics scripts. Example switching and command copying run locally in the browser; no documents are uploaded.

GitHub Pages workflow: `.github/workflows/pages.yml`. For a public repository, select GitHub Actions under Settings → Pages → Build and deployment → Source. Changes to `site/` on `main` then deploy automatically.

Both language versions are deployed: [Chinese website](https://chainsy3.github.io/universal-rag-chunker/) and [English website](https://chainsy3.github.io/universal-rag-chunker/en.html). The navigation links switch between `index.html` and `en.html`. Each language version links to its corresponding `.cn.md` or `.en.md` documentation.

For local preview, run `python -m http.server 8765 --directory site` from the project root and open http://localhost:8765 . This is a project introduction, without online file parsing.
