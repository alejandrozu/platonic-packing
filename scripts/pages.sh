#!/bin/bash
# Publish the website in site/ (built by scripts/site.py) to the gh-pages branch, served at https://polyhedrainpolyhedra.wiki
# (custom domain from site/CNAME). On GitHub the same deploy is done by .github/workflows/site.yml.
# Uses a separate clone in .pages/ (git-ignored) so the main working tree is never switched.
cd "$(dirname "$0")/.."
[ -f site/index.html ] || exit 0
if [ ! -d .pages/.git ]; then
  rm -rf .pages; git clone -q --branch gh-pages --single-branch "$(git remote get-url origin)" .pages || exit 1
fi
cd .pages
git fetch -q origin gh-pages && git reset -q --hard origin/gh-pages
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -r ../site/. .; touch .nojekyll
git add -A
git diff --cached --quiet && { echo "pages: unchanged"; exit 0; }
git -c user.name="$(git -C .. log -1 --format=%an)" -c user.email="$(git -C .. log -1 --format=%ae)" commit -q -m "Update site ($(date '+%Y-%m-%d %H:%M'))

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015sjhNzKTinVQnSnofRcCoP"
if timeout 90 git push -q origin gh-pages; then echo "pages: pushed"; else echo "pages: PUSH-FAILED"; fi
