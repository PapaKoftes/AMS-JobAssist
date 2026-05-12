# Phase 11.2 Testing Guide

Complete instructions for testing the Tool 2 Trainer Dashboard web UI.

---

## Quick Start (5 minutes)

### Step 1: Start the Backend
```bash
cd C:\Github\PapaKoftes\tool-2-trainer-dashboard\src\backend
python app.py
```

Expected output:
```
✓ Trainer dashboard database initialized
✓ Serving at http://127.0.0.1:8001
```

### Step 2: Open the Application
```
http://localhost:8001
```

You should see the AMS JobAssist Trainer Dashboard with the Dashboard view active.

### Step 3: Quick Feature Test
- [ ] Dashboard loads with 0 participants
- [ ] Import button is visible
- [ ] Navigation menu appears
- [ ] Settings page accessible

---

## Full Test Suite

### Test 1: Import CVs

**Objective**: Verify file upload and CV import works

**Steps**:
1. Click "📥 Import CVs" button on dashboard
2. Enter cohort name: `Test-Cohort-2026`
3. Drag-and-drop a .json file from Tool 1, OR
4. Click drop zone to browse and select file
5. Click "📥 Import CVs" button

**Expected Result**:
- Success message appears
- Count of imported CVs shown
- Message disappears after 3 seconds
- Form clears for next import

**Sample .json File** (save as `test_cv.json`):
```json
{
  "user_id": "test_user_001",
  "name": "Max Mustermann",
  "email": "max@example.com",
  "interview_path": "unemployed",
  "background": "I worked in manufacturing for 5 years",
  "experience": "I managed a team of 3 people and improved efficiency by 20%",
  "skills": "Microsoft Excel, German, English, Problem Solving",
  "education": "Gymnasium, Abitur, VHS Programming Course",
  "languages": "German, English, Basic Spanish",
  "overall_quality": 0.82,
  "ready_for_export": true,
  "language_output_primary": "de",
  "language_output_secondary": "en"
}
```

---

### Test 2: View Participants List

**Objective**: Verify participant list loads and displays correctly

**Prerequisites**: At least one CV imported (see Test 1)

**Steps**:
1. Click "👥 Participants" in navigation
2. Observe the participant table
3. Search: Type "Max" in search box
4. Filter by status: Select "Pending"
5. Filter by cohort: Select "Test-Cohort-2026"

**Expected Result**:
- Table shows all imported participants
- Search filters by name/email
- Status filter works
- Cohort filter works
- Select All checkbox selects/deselects all visible rows

---

### Test 3: View Participant Detail

**Objective**: Verify detail view shows CV data correctly

**Prerequisites**: At least one participant imported

**Steps**:
1. In Participants view, click "View" button for a participant
2. Observe the detail page layout
3. Check participant header info
4. Compare original vs polished CV

**Expected Result**:
- Detail view loads with participant name
- Status badge shows current status
- Side-by-side comparison visible
- Original answers on left (grayed out)
- Polished CV on right
- Sections: Background, Experience, Skills, Education, Languages

---

### Test 4: Inline Editing

**Objective**: Verify edit functionality works

**Prerequisites**: Detail view open with a participant

**Steps**:
1. Click on any "Polished CV" section text (right side)
2. Text becomes editable (textarea appears)
3. Type some new text
4. Click "Save" button
5. Observe text update

**Expected Result**:
- Clicking CV section makes it editable
- Textarea appears with current text
- Save button becomes visible
- Cancel button available
- Save updates the display immediately
- After save, can click again to edit

---

### Test 5: Approval Workflow

**Objective**: Verify approval status and feedback works

**Prerequisites**: Detail view open with a participant

**Steps**:
1. Scroll to "Approval & Feedback" section
2. Change status from "Pending" to "Approved"
3. Add feedback: "Good CV, approved for export"
4. Click "💾 Save & Approve"
5. Observe success message
6. Go back to participants and verify status changed

**Expected Result**:
- Status dropdown works
- Feedback textarea accepts text
- Save button triggers API call
- Success message appears: "✓ Approval saved"
- Participant status updates in list
- Status badge changes color to green (approved)

---

### Test 6: Bulk Actions

**Objective**: Verify bulk approve/reject works

**Prerequisites**: 2+ participants in list

**Steps**:
1. Go to Participants view
2. Check "Select All" checkbox
3. Click "✅ Approve Selected"
4. Confirm in dialog: "Approve X participants?"
5. Verify all participants marked as approved

**Alternative - Bulk Reject**:
1. Select some participants (check individual boxes)
2. Click "❌ Reject Selected"
3. Enter rejection reason
4. Verify status changed

**Expected Result**:
- Select All checkbox selects all visible rows
- Bulk action buttons enabled when rows selected
- Dialog prompts for confirmation
- All selected participants updated
- Status updated in table immediately

---

### Test 7: Dashboard Metrics

**Objective**: Verify metrics calculate correctly

**Prerequisites**: 3+ participants with mixed statuses

**Setup**:
- Approve some participants
- Reject some
- Leave some pending

**Steps**:
1. Go to Dashboard
2. Select cohort from dropdown
3. Click "🔄 Refresh"
4. Observe metrics update

**Expected Result**:
- Total Participants: Count all
- Completed: Count approved only
- Completion %: (completed/total) * 100
- Avg Quality: Average of all quality scores
- Pending Review: Count pending only
- Activity Feed: Shows recent updates

---

### Test 8: Search and Filter

**Objective**: Verify filtering combinations work

**Prerequisites**: 5+ participants with mixed data

**Steps**:
1. Participants view
2. Search: "max" (case-insensitive)
3. Filter status: "Approved"
4. Filter cohort: "Test-Cohort-2026"
5. Verify results match all criteria

**Expected Result**:
- Search works on name and email
- Filters combine (AND logic, not OR)
- Results update instantly
- Clear text to reset search
- Change filters to update results

---

### Test 9: Settings Persistence

**Objective**: Verify settings save across page reloads

**Steps**:
1. Go to Settings
2. Change trainer name: "John Trainer"
3. Select language: "English"
4. Select format: "PDF"
5. Reload page (F5)
6. Go back to Settings
7. Verify trainer name still shows "John Trainer"

**Expected Result**:
- Settings save to localStorage
- Trainer name shown in navbar
- Settings persist across reloads
- No data loss on page refresh

---

### Test 10: Responsive Design

**Objective**: Verify UI works on different screen sizes

**Steps**:

#### Desktop (1400px+)
1. Open DevTools (F12)
2. Close DevTools (or set width to desktop)
3. Verify full layout displays
4. Side-by-side CV comparison visible

#### Tablet (768px - 1024px)
1. DevTools → Toggle device toolbar
2. Select iPad or similar
3. Verify layout stacks appropriately
4. Navigation wraps if needed
5. Buttons still clickable

#### Mobile (< 768px)
1. DevTools → Mobile view (375px width)
2. Verify single-column layout
3. Navigation stacks vertically
4. Tables may become vertical lists
5. All buttons accessible

**Expected Result**:
- Responsive breakpoints work (768px, 1024px)
- UI adapts gracefully
- Touch targets large enough (> 44px)
- No horizontal scroll (except tables)

---

### Test 11: Error Handling

**Objective**: Verify errors display properly

**Steps**:

#### Test Invalid File Upload
1. Import view
2. Try uploading a .txt file
3. Observe error message

#### Test Missing Cohort
1. Import view
2. Don't enter cohort name
3. Click import
4. Observe validation error

#### Test API Failure (Simulate)
1. Stop backend server
2. Try any action (refresh, import, etc.)
3. Observe error message in UI

**Expected Result**:
- Invalid file type rejected
- Missing fields validated before send
- API errors show in UI (not just console)
- User knows what went wrong
- Can recover and retry

---

### Test 12: Performance

**Objective**: Verify UI performs well

**Prerequisites**: 50+ participants loaded

**Steps**:
1. DevTools → Performance tab
2. Load participants list
3. Search/filter (should be instant)
4. Scroll through list
5. Click into detail view
6. Edit CV section

**Check**:
- List renders in < 1 second
- Search/filter responses instant (< 100ms)
- Detail view loads in < 500ms
- Smooth scrolling
- No lag when clicking

**Tools**:
- DevTools Performance tab
- DevTools Console (look for slow messages)
- Network tab (check API response times)

---

## Acceptance Criteria

### Must Pass ✅
- [ ] All 9 views load without errors
- [ ] Navigation between views works
- [ ] Import uploads files correctly
- [ ] Participant list displays data
- [ ] Detail view shows CV comparison
- [ ] Inline editing saves changes
- [ ] Approval updates status
- [ ] Bulk actions work
- [ ] Responsive on mobile/tablet/desktop
- [ ] Errors display clearly

### Should Pass ⚠️
- [ ] Performance acceptable
- [ ] Settings persist
- [ ] Metrics calculate correctly
- [ ] Filters work together
- [ ] Dashboard updates on refresh

### Nice to Have 🎯
- [ ] Keyboard navigation (Tab, Enter)
- [ ] Accessibility (screen readers)
- [ ] Print CV works
- [ ] Dark mode

---

## Bug Report Template

If you find an issue:

```
Title: [Brief description]

Steps to Reproduce:
1. 
2. 
3. 

Expected Result:
[What should happen]

Actual Result:
[What actually happened]

Screenshot/Video:
[If applicable]

Browser:
[Chrome/Firefox/Safari + version]

Environment:
[localhost:8001]
```

---

## Performance Baseline

After testing, record these metrics:

```
Dashboard Load Time:        ___ ms
List Load (50 items):       ___ ms
Detail View Load:           ___ ms
Search Response (instant):  ___ ms
Approval Save:              ___ ms
Memory Usage (idle):        ___ MB
Memory Usage (full list):   ___ MB
```

---

## Sign-off

**Tester Name**: ________________  
**Date**: ________________  
**Result**: ☐ PASS  ☐ FAIL  

**Comments**:
```
[Notes on any issues found]
```

---

## Next Steps

If all tests pass:
1. Ready for Phase 11.3 integration testing
2. Can proceed with PyInstaller packaging
3. Can generate user documentation

If tests fail:
1. Document issues clearly
2. Fix in development branch
3. Re-test before proceeding

---

**Happy Testing!** 🚀
