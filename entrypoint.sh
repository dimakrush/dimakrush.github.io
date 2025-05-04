#!/usr/bin/env bash
set -e
: "${GITHUB_TOKEN?Need to set GITHUB_TOKEN env var}"
REPO=${GITHUB_REPOSITORY:-"dimakrush/dimakrush.github.io"}
BRANCH=${TARGET_BRANCH:-"main"}

echo "Starting process..."

# 1) Scrape & write CSV
echo "Running Python script..."
python3 scripts/casualties.py

# 2) Copy CSV into docs/
echo "Copying CSV into docs/…"
cp russian_casualties.csv docs/

# 3) Render Quarto in docs/
echo "Rendering Quarto document in docs/…"
cd docs
quarto render project-orc-losses.qmd
cd ..

# 4) Stage, commit & push
echo "Staging updated HTML & assets…"
git add docs/project-orc-losses.html docs/project-orc-losses_files/

echo "Committing & pushing…"
git config user.name  "dimakrush"
git config user.email "122113936+dimakrush@users.noreply.github.com"
git commit -m "chore: daily rebuild $(date +'%F')" --allow-empty
git remote set-url origin \
  https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git
git push origin ${BRANCH}

echo "Process completed."
