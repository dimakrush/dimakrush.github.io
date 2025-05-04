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

# 2) Render Quarto to docs/
echo "Rendering Quarto document..."
quarto render project-orc-losses.qmd --to html --output-dir docs

# 3) Stage only the new HTML and its assets
echo "Staging updated HTML & assets..."
git add docs/project-orc-losses.html docs/project-orc-losses_files/

# 4) Commit & push if there’s anything staged
if ! git diff --cached --quiet HEAD; then
  echo "Changes detected → committing and pushing…"

    git config user.name  "dimakrush"
    git config user.email "122113936+dimakrush@users.noreply.github.com"


  # Use the token to push over HTTPS
  git remote set-url origin \
    https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git

  git commit -m "chore: daily rebuild $(date +'%F')"
  git push origin ${BRANCH}

  echo "Successfully pushed changes."
else
  echo "No changes in docs → nothing to do."
fi

echo "Process completed."
