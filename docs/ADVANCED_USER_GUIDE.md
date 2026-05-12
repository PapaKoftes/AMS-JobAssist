# AMS JobAssist - Advanced User Guide

**Version**: 1.0  
**Date**: 2026-05-02  
**Audience**: Trainers, Managers, Power Users  

---

## Table of Contents

1. [Advanced Interview Techniques](#advanced-interview-techniques)
2. [Quality Optimization](#quality-optimization)
3. [Batch Operations](#batch-operations)
4. [Reporting & Analytics](#reporting--analytics)
5. [Integration with External Tools](#integration-with-external-tools)
6. [Customization](#customization)
7. [Advanced Troubleshooting](#advanced-troubleshooting)

---

## Advanced Interview Techniques

### Multi-Session Management

**Scenario**: Participant returns after a break (next day, next week)

**How it works**:
1. Participant enters their user ID when starting Tool 1
2. System automatically resumes where they left off
3. They see progress bar showing how far they got
4. Can continue from any question

**Best Practice**: Encourage participants to remember their user ID
- Suggest format: FirstName_LastName or Email prefix
- Write it down on printed materials

### Re-asking Weak Answers

**When Tool 1 re-asks**:
- Answer is < 10 words
- Answer is too vague ("good worker")
- Answer lacks specific details

**Example flow**:
```
Trainer: "What tools did you use?"
Participant: "Computers"
↓
System: "Can you be more specific? What software or programs?"
↓
Participant: "Microsoft Excel, Word, and QuickBooks"
↓
System: "Great! That's much clearer."
```

**For trainers**: Encourage specific examples during in-person interview
- Instead of "Tell me about your job"
- Ask "What did you do on a typical Tuesday?"

### Language Handling

**Tool 1 accepts**:
- Any of 14+ languages (German, English, Polish, Italian, etc.)
- Mixed languages in same answer (e.g., "Ich use Microsoft Excel")
- Slang, colloquial speech, broken grammar

**Tool 1 normalizes to**:
- Standard German for CV
- Clear English translation
- Native language version (if different)

**Example transformation**:
```
Input (Serbian): "Ja radim sa Excel i Word, i vodim ljude"
↓ Detected: Serbian
↓
Output (German): "Ich arbeite mit Microsoft Excel und Word. 
                  Ich leite Menschen."
↓
Output (English): "I work with Microsoft Excel and Word. 
                   I lead people."
↓
Output (Serbian): "Ja radim sa Microsoft Excel i Word. 
                   Ja vodim ljude."
```

### Interview Path Selection

**Available paths**:
1. **Unemployed** - Recently lost job, seeking new employment
2. **Career Switch** - Changing industries or roles
3. **Student** - Recent graduate, seeking first job
4. **Career Pause** - Returning after break (parenting, health, etc.)
5. **Other** - Doesn't fit above categories

**Trainer's role**: Help participant select appropriate path
- Affects question focus and wording
- Shapes suggested skills and strengths
- Can be changed later in Tool 2

**Changing path after import**:
1. Tool 2 → Participants → Select participant
2. Edit "Interview Path" field
3. Re-answer relevant questions if needed

---

## Quality Optimization

### Understanding Quality Scores

**Scale**: 0.0 - 1.0 (0% to 100%)

**Components**:
- **Verb Strength** (30%): Uses active verbs (led, managed, created, etc.)
- **Skill Clarity** (30%): Specific skills identified and extracted
- **Structure** (20%): Good sentence structure, clear organization
- **Detail Level** (20%): Sufficient length and specific examples

**Example scores**:

| Score | Interpretation | Example |
|-------|---|---------|
| 0.6-0.65 | Below Average | "I worked in a shop" |
| 0.65-0.75 | Acceptable | "I worked retail, helped customers" |
| 0.75-0.85 | Good | "Managed customer service team of 3, improved satisfaction by 15%" |
| 0.85+ | Excellent | "Led team of 5 customer service reps, reduced complaint resolution time by 20%, maintained 95% satisfaction rating" |

### Improving Weak Answers

**Trainer strategies** (during in-person interview):

1. **Ask follow-up questions**
   - Q: "What did you do?"
   - A: "I worked in a factory"
   - Follow-up: "What was your specific job? What did you make?"
   - A: "I assembled car parts. I worked on the production line."
   - **Better answer generates higher quality score**

2. **Probe for impact**
   - Q: "What was important in your job?"
   - A: "Being accurate"
   - Follow-up: "How did that show? Can you give an example?"
   - A: "I checked every 10th part I assembled. Out of 500 parts, only 2 had errors."

3. **Extract hidden skills**
   - "Tell me about a time something went wrong"
   - "How did you solve it?"
   - "Who did you work with?"
   - → Reveals problem-solving, teamwork, leadership

### Batch Re-scoring

If you update questions or answer text in Tool 2:

1. Select affected participants
2. Use "Re-score Selected" (if available)
3. System recalculates quality scores
4. Review results for significant changes

**Note**: Manual editing in Tool 2 doesn't change Tool 1 data

---

## Batch Operations

### Bulk Import Multiple CVs

**Scenario**: Received CVs from Tool 1 for 20 participants

**Method 1: ZIP file** (recommended for 5+ participants)
1. Collect all .json files from participants
2. Create ZIP file in Windows:
   - Select all .json files
   - Right-click → Send to → Compressed (ZIP)
   - Name it `Cohort-Q2-2026.zip`
3. Tool 2 → Import CVs
4. Upload ZIP file
5. All participants imported in one action

**Method 2: Single file** (for 1-2 participants)
1. Get individual .json file from participant
2. Tool 2 → Import CVs
3. Upload single file
4. One participant imported

**Method 3: Bulk export from Tool 1** (future feature)
Currently not available, but coming in next version

### Bulk Approval

**Scenario**: All 20 participants submitted good CVs

**Quick approval**:
1. Tool 2 → Participants
2. Click checkbox next to each name (or "Select All" button)
3. Click "✅ Approve Selected"
4. Confirm action
5. All selected participants marked as "Approved" instantly

**With notes**:
1. Select participants
2. Click "Approve Selected"
3. Enter notes: "Batch-approved 2026-Q2 cohort"
4. Click "Save"
5. Notes apply to all selected participants

**Filtered bulk approval**:
1. Filter by Status: "Pending"
2. Filter by Cohort: "Batch-2026-Q2"
3. "Select All" (shows only filtered results)
4. "Approve Selected"
5. Only matching participants are affected

### Bulk Export

**Scenario**: Completed review, need to export all approved CVs

**Export all approved**:
1. Participants list
2. Filter Status: "Approved"
3. Click "📤 Export Selected"
4. Choose format: PDF, DOCX, or JSON
5. Choose language: German, English, or Native
6. Click "Download"
7. Get all as PDF files in a ZIP

**Export specific cohort**:
1. Filter Cohort: "Batch-2026-Q2"
2. Select participants manually (or "Select All" for filtered view)
3. Export as above

**Export with metadata**:
1. Export includes approval date, trainer name
2. Useful for records and reporting
3. Filename pattern: `Cohort_Batch-2026-Q2_2026-05-02.zip`

---

## Reporting & Analytics

### Dashboard Metrics

The Tool 2 Dashboard shows at a glance:

**Total Participants**: All imported for this system
**Completion Rate**: % that have been approved/rejected (vs pending)
**Average Quality**: Mean quality score across all participants
**Recent Activity**: Last 10 approvals/rejections with timestamps

**Using metrics**:
- **Low completion rate** → Need more trainer time
- **Low average quality** → Participants need interview coaching
- **High quality**: → Cohort is strong, CV-ready

### Cohort-Level Analytics

Each cohort (Batch-2026-Q2, etc.) shows:

- **Total participants** in cohort
- **% Approved** → Ready for job matching
- **% Pending** → Still in review
- **% Rejected** → Need to re-interview
- **Average quality** for this cohort only
- **Completion date** prediction (if data available)

**Using cohort metrics**:
- Compare quality across training sessions
- Identify which cohorts had strongest participants
- Spot trends in cohort performance

### Export Report

**Available reports** (under Dashboard → Reports):

1. **Participation Report**
   - Who completed, who didn't
   - Interview paths selected
   - Time spent per participant

2. **Quality Report**
   - Participants by quality score range
   - Skill distributions
   - Language detection patterns

3. **Approval Report**
   - Approvals by trainer and date
   - Rejections and reasons
   - Timeline of reviews

4. **Export all to CSV** (for external analysis)
   - Import into Excel, Google Sheets
   - Create custom pivot tables
   - Compare across years

---

## Integration with External Tools

### Export to Excel

**Scenario**: Need to track participants in Excel alongside other data

**Steps**:
1. Tool 2 → Dashboard → Reports → "Export Participants CSV"
2. Opens CSV file with columns: ID, Name, Email, Status, Quality, Path
3. Save as `.xlsx` in Excel
4. Use Excel formulas to merge with other data

**Template columns added**:
```
A: Last Name
B: First Name
C: Email
D: CV Quality (0.00-1.00)
E: Approval Status
F: Approved By (trainer name)
G: Approved Date
H: Cohort
I: Export Path
```

### Export to Google Sheets

1. Export CSV from Tool 2
2. Open Google Drive
3. Google Sheets → Import sheet
4. Select CSV file
5. Data imported, shareable with team

### Integrate with Job Board

**Workflow**:
1. Approve participants in Tool 2
2. Export as PDF
3. Upload PDFs to job matching system
4. System matches participants to open positions
5. Notify successful matches

**Status tracking**:
- Export date, recipient, status tracked in Tool 2 notes
- "Exported to JobBoard 2026-05-05"

---

## Customization

### Custom Interview Questions

**Current**: Tool 1 uses standardized questions (20 per path)

**Future customization**:
- Edit questions per training program
- Add organization-specific questions
- Reorder question sequence
- Adjust difficulty

**For now**: Use trainer notes to supplement

### Skill Taxonomy

**Standard skills** extracted (60+ predefined):
- Microsoft Office, Python, Customer Service, Leadership, etc.

**Custom skills**:
- Edit Tool 2 participant detail
- Add custom skills in notes: "Additional skills: CAD, CNC"
- Trainer notes visible in all exports

### Branding

**Current**: Generic AMS branding on PDF/DOCX exports

**Customization options** (contact support):
- Organization logo on exports
- Custom colors matching your brand
- Footer with training center contact info
- Header with certification/completion mark

---

## Advanced Troubleshooting

### Participant Lost Their Session

**Scenario**: Participant closed Tool 1 and forgot their User ID

**Recovery**:
1. Participant tries to restart with new ID
   - System sees new user, starts fresh interview
   - Original data still in Tool 1 database
2. Trainer can manually search old database
   - Contact IT/admin for database query
   - Recover lost user ID
   - Participant resumes with original ID

**Prevention**: Print user ID sheets for participants to keep

### Duplicate Participants in Tool 2

**Cause**: Same participant imported twice with different .json files

**Detection**:
1. Tool 2 → Participants
2. Search by email
3. If multiple entries appear

**Resolution**:
1. Contact admin (deletion not available in UI)
2. Admin deletes duplicate record from database
3. Keep most recent version (higher quality score)

### Data Doesn't Sync Between Tools

**Scenario**: Updated CV in Tool 2, but changes don't appear in Tool 1

**This is expected**: Tools are independent
- Tool 1: Source of truth for participant data
- Tool 2: Review and approval layer
- Updates in Tool 2 don't feed back to Tool 1

**Workflow**:
1. Participant completes interview in Tool 1
2. Exports CV data
3. Trainer imports into Tool 2
4. Trainer makes minor edits in Tool 2
5. Exports final CV for use
6. Tool 1 data unchanged (as backup)

### Performance Issues with Large Cohorts

**Slow when**: 500+ participants in Tool 2

**Solutions**:
1. Archive old cohorts (move data out of active tool)
2. Close browser tabs with Tool 2 open (reduces memory)
3. Increase computer RAM
4. Use filtering:
   - Filter by cohort (shows fewer participants)
   - Filter by status (faster list loading)

### Import Fails Silently

**Scenario**: Import form says "completed" but no participants appear

**Causes & fixes**:
1. **Invalid JSON format**
   - Re-export from Tool 1
   - Verify file opens in text editor (shows readable JSON)
   - Try importing single file first

2. **Duplicate user IDs**
   - Participant already imported
   - Tool 2 silently skips duplicates
   - Check existing participants before re-importing

3. **Missing required fields**
   - Tool 1 export incomplete
   - Re-run interview in Tool 1
   - Export again

4. **File too large**
   - ZIP with 1000+ files may fail
   - Split into smaller batches
   - Import in groups of 100

---

## Tips for Trainers

### Before Training Session

- [ ] Brief participants on interview process
- [ ] Explain they don't need perfect grammar
- [ ] Show examples of good answers
- [ ] Distribute user ID sheets (for resume capability)
- [ ] Test tools start correctly
- [ ] Have backup laptop/PC available

### During Training Session

- [ ] Have trainer laptop open with Tool 2
- [ ] Display before/after examples on projector
- [ ] Encourage specific, detailed answers
- [ ] Remind participants: answers will be improved
- [ ] Note participants who struggle (offer 1-on-1 help)

### After Training Session

- [ ] Collect all .json files from participants
- [ ] Import into Tool 2
- [ ] Do quick review for quality issues
- [ ] Approve and export for job board
- [ ] Send copies to participants
- [ ] Backup data to external drive
- [ ] Document training outcomes

### Quality Coaching

When participants ask "Is this good enough?":

**Poor examples** (< 0.65 score):
- "I worked there"
- "Good at my job"
- "Helped customers"

**Better examples** (0.75+ score):
- "Managed inventory system for automotive parts warehouse, reducing stock errors from 5% to 1%"
- "Trained 3 new team members on safety protocols and equipment operation"
- "Improved customer satisfaction scores from 80% to 92% through proactive problem-solving"

**Coaching tip**: "Tell me a story about a day at work, what happened, what you did"

---

## Version History

**v1.0** (2026-05-02)
- Advanced techniques documentation
- Quality optimization guides
- Batch operations instructions
- Reporting and analytics overview
- Integration examples
- Troubleshooting for complex scenarios

---

**For questions about advanced features**: Contact your AMS training coordinator or submit feature request to support@ams-jobassist.local
