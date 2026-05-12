# AMS JobAssist - Trainer Quick Start Guide

**Duration**: 10 minutes  
**Audience**: AMS Trainers  
**Tools Needed**: Windows PC, browser, participant CVs from Tool 1

---

## What is AMS JobAssist?

A two-tool system for managing participant CVs:
- **Tool 1**: Participants complete interview → generate polished CV
- **Tool 2**: Trainers review CVs → approve → export for records

---

## Starting the Application

### Option 1: Batch Menu (Recommended)
```
Double-click: ams_jobassist.bat
```

Choose **[2] Starten** (or **[1] Installieren und Starten** on first use).  
This starts both tools and opens your browser automatically.

> ⚠️ Single-click `.exe` packaging is on the roadmap but not yet complete.  
> Until then, use the `.bat` launcher above.

### Option 2: Manual (Development)
```bash
python launcher.py
```

Wait 5-10 seconds for startup, then open:
- Tool 1 (Participants): http://localhost:8000
- Tool 2 (Trainers): http://localhost:8001

---

## Your Workflow: 5 Steps

### Step 1: Get CVs from Participants
Participants use **Tool 1 (CV Maker)** to:
1. Complete a guided interview (20-30 minutes)
2. See their answers improved in real-time
3. Export as JSON file

**You receive**: One or more .json files

### Step 2: Import CVs into Tool 2
1. Open **Tool 2 (Trainer Dashboard)**
2. Click "📥 Import CVs"
3. Enter cohort name (e.g., "Batch-2026-Q2")
4. Drag-and-drop the .json file or click to browse
5. Click "Import"

**Result**: CVs now in your dashboard

### Step 3: Review Participants
1. Go to "👥 Participants"
2. You see a table of all imported participants
3. Click "View" to see their CV

### Step 4: Review CV Side-by-Side
When viewing a participant:
- **Left side**: Original interview answers (read-only)
- **Right side**: Polished CV (you can edit)

You can:
- **Click any section** to edit it
- **Save changes** immediately
- Compare original vs improved version

### Step 5: Approve or Request Changes
At the bottom:
1. Change **Status**:
   - ✅ Approved - CV is good
   - ⚠️ Needs Changes - Participant must revise
   - ❌ Rejected - CV not suitable
2. Add **Notes** (optional feedback)
3. Click "💾 Save & Approve"

**That's it!** Status updates instantly.

---

## Key Features

### Dashboard
- See metrics at a glance
- Total participants, % completed, avg quality
- Recent activity feed

### Participant List
- **Search**: Type name or email
- **Filter by Status**: Approved, pending, rejected
- **Filter by Cohort**: Different training groups
- **Bulk Actions**: Approve 10+ at once

### Detail View
- Side-by-side CV comparison
- Click to inline-edit
- Approve/reject with notes
- Tracks who approved and when

### Import Multiple Files
- Import one .json file
- OR upload .zip with multiple files
- Creates participant record automatically

---

## Common Tasks

### Task 1: Batch Approve Participants
1. Participants list
2. Check "Select All" ✓
3. Click "✅ Approve Selected"
4. Confirm
5. Done - all approved instantly

### Task 2: Give Feedback
1. Open participant detail
2. Click CV section to edit
3. Edit the text
4. Click "Save"
5. Add trainer notes at bottom
6. Save again

### Task 3: Export All CVs
1. Participants list
2. Select participants with checkboxes
3. Click "📤 Export Selected"
4. Choose format (PDF, DOCX, JSON)
5. Download

### Task 4: See Quality Scores
- Dashboard → metrics show average quality
- Participant list → Quality column
- Detail view → Quality badge

---

## Troubleshooting

### "Can't connect to server"
- Wait 10 seconds after starting the launcher
- Check: Is the terminal/command window still open? Do not close it while working.
- Port conflict? Close other apps using ports 8000 or 8001

### "Import fails"
- Check file is .json or .zip
- Cohort name can't be empty
- File must be valid JSON from Tool 1

### "Can't edit CV"
- Click the text on the **right side** (polished version)
- Not the left side (original - read-only)

### "Changes not saving"
- Verify the "Save" confirmation appeared
- Check the terminal window for error messages
- Refresh page if stuck — your data is stored in the local database

### App crashed or frozen
- Close the terminal window
- Run `ams_jobassist.bat` again and choose [2] Starten
- Restart the computer if the port is stuck

---

## Tips for Trainers

✅ **DO**:
- Import CVs regularly (weekly or as you receive them)
- Give constructive feedback in trainer notes
- Use bulk approve for quick batches
- Review quality scores to spot patterns

❌ **DON'T**:
- Edit only to "fix grammar" - trainer notes are better
- Close the .exe while reviewing (use "Back" button)
- Share passwords or credentials
- Delete cohorts (data is permanent)

---

## Your Data

### Where is everything saved?
- **Database**: `ams_trainer.db` (in application folder)
- **Automatic backup**: Keep a copy of .db file weekly

### Can I edit later?
Yes - open Tool 2 anytime, participant data stays forever

### How do I export final CVs?
1. Dashboard → "📤 Export Batch" (future feature)
2. OR Participants → Select → "Export Selected"
3. Choose PDF/DOCX/JSON format
4. Download

---

## Settings

**In Tool 2 → Settings**:
- **Trainer Name**: Your name (appears in approvals)
- **Default Language**: German/English/Native
- **Default Format**: PDF/DOCX/JSON
- **Clear Cache**: If app acts weird

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Tab | Move between fields |
| Enter | Save in edit mode |
| Esc | Cancel edit |
| Ctrl+A | Select all in table |
| F5 | Refresh page |

---

## Support

**Getting Help**:
1. Check "Troubleshooting" section above
2. Review the FAQ
3. Contact IT/developer

**Error Messages**:
- **"Participant not found"** → They may have been deleted
- **"Import failed"** → Check file format
- **"Cannot save"** → Connection issue, try again

---

## Summary

```
Start → Import CVs → Review → Approve/Reject → Export

Time per participant: 5-10 minutes
Time to train: 1-2 hours
Ongoing: 15 minutes/week
```

---

## Next Steps

1. ✅ Install and run launcher
2. ✅ Import one test CV
3. ✅ Review and approve
4. ✅ Try bulk operations
5. ✅ Check settings
6. ✅ You're ready!

---

**Questions?** See [FAQ.md](FAQ.md) or [AMS_INSTRUCTOR_GUIDE.md](AMS_INSTRUCTOR_GUIDE.md).  
**Something broken?** File an issue on GitHub or contact your administrator.
