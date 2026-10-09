#!/bin/bash
# Checkpoint for the copy on Alejandro's computer: commit the archive locally (if changed) and write an incremental git
# bundle (last synced commit .. HEAD) to /mnt/user-data/outputs/sync.bundle. Prints "BUNDLE <from> <to>" or "UPTODATE <head>".
# After the bundle is applied on the computer, record the synced commit with:  git rev-parse HEAD > state/.device_synced
cd "$(dirname "$0")/.."
exec 9> state/.gitlock; flock 9
git add state/best state/attempts.jsonl PROGRESS.md STATUS.md EXPERIMENT_LOG.md scripts src docs README.md .gitignore 2>/dev/null
if ! git diff --cached --quiet; then
  git commit -q -m "Checkpoint: search archive $(date '+%Y-%m-%d %H:%M')

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015sjhNzKTinVQnSnofRcCoP"
fi
head=$(git rev-parse HEAD); from=$(cat state/.device_synced 2>/dev/null)
if [ "$from" = "$head" ]; then echo "UPTODATE $head"; exit 0; fi
mkdir -p /mnt/user-data/outputs
git bundle create -q /mnt/user-data/outputs/sync.bundle "$from..main" 2>/dev/null || git bundle create -q /mnt/user-data/outputs/sync.bundle main
echo "BUNDLE ${from:-none} $head $(du -h /mnt/user-data/outputs/sync.bundle | cut -f1)"
