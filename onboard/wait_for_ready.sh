#!/usr/bin/env bash
# Onboarding helper: waits for user to place files and type "ready"

echo "👋 Hi! I'm your Job Getter Bot. Before I start hunting for roles, I'd like to get to know you better."
echo ""
echo "Please place your files in the following folders (drag-and-drop or File Explorer):"
echo "  • Resumes (PDF, DOCX, TXT)   → $HOME/Documents/job-getter/onboard/processing/resumes/"
echo "  • Cover letters (PDF, DOCX, TXT) → $HOME/Documents/job-getter/onboard/processing/cover_letters/"
echo ""
echo "When you're done, type \"ready\" and press Enter."
while true; do
    read -r ans
    if [[ "$ans" == "ready" || "$ans" == "Ready" ]]; then
        echo "✅ Thanks! Processing your documents..."
        break
    else
        echo "Please type \"ready\" when you've placed your files."
    fi
done