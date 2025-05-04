#!/usr/bin/env bash
set -e

: "${GITHUB_TOKEN?Need to set GITHUB_TOKEN env var}"
REPO=${GITHUB_REPOSITORY:-"dimakrush/dimakrush.github.io"}
BRANCH=${TARGET_BRANCH:-"main"}

echo "Starting process..."

echo "1) Scraping…"
python3 scripts/casualties.py

echo "2) Rendering Quarto…"
quarto render project-orc-losses.qmd --to html --output-dir docs

echo "3) Staging updated HTML & assets…"
git add docs/project-orc-losses.html docs/project-orc-losses_files/

echo "4) Forcing a commit & push (HTML-only)…"
git config user.name  "dimakrush"
git config user.email "122113936+dimakrush@users.noreply.github.com"

# allow-empty makes sure Git will always create a commit, even if the HTML
# hadn’t structurally changed (so you get a new timestamped commit every run)
git commit -m "chore: daily rebuild $(date +'%F')" --allow-empty

# push over HTTPS using your token
git remote set-url origin \
  https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git
git push origin ${BRANCH}

echo "Done."
