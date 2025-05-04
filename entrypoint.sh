#!/usr/bin/env bash
set -e

# Fail early if token is missing
: "${GITHUB_TOKEN?Need to set GITHUB_TOKEN env var}"

# Your repo slug and branch
REPO=${GITHUB_REPOSITORY:-"dimakrush/dimakrush.github.io"}
BRANCH=${TARGET_BRANCH:-"main"}

echo "Starting process..."

# 1) Scrape & write CSV
echo "Running Python script..."
python3 scripts/casualties.py

# 2) Render Quarto in docs/
echo "Rendering Quarto document in docs/..."
cd docs
quarto render project-orc-losses.qmd    # will produce project-orc-losses.html + _files/
cd ..

# 3) Stage only the new HTML and its assets
echo "Staging updated HTML & assets..."
git add docs/project-orc-losses.html docs/project-orc-losses_files/

# 4) Always commit & push the HTML
echo "Committing & pushing changes…"
git config user.name  "dimakrush"
git config user.email "122113936+dimakrush@users.noreply.github.com"

# --allow-empty ensures a commit even if contents didn’t change
git commit -m "chore: daily rebuild $(date +'%F')" --allow-empty

# Push over HTTPS using the token
git remote set-url origin \
  https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git
git push origin ${BRANCH}

echo "Process completed."
