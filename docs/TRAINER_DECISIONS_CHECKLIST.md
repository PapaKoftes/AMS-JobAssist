# AMS JobAssist — Trainer Decisions Checklist

**Before implementation, work with AMS instructors to define these.**

These decisions shape the tool and determine success. Answer together with your AMS partner(s).

---

## A. INTERVIEW DESIGN

### A1: Interview Paths
Currently planned: 5 paths

- [ ] **Unemployed / First Job Seeker**
  - Focus: Education + skills + internships
  - Realistic for your participants? ○ Yes ○ No ○ Modify

- [ ] **Career Switch**
  - Focus: Recent job + new direction
  - Realistic? ○ Yes ○ No ○ Modify

- [ ] **Student / Recent Graduate**
  - Focus: Education + projects + internships
  - Realistic? ○ Yes ○ No ○ Modify

- [ ] **Career Pause / Returning**
  - Focus: Last job + gap + new direction
  - Realistic? ○ Yes ○ No ○ Modify

- [ ] **Catch-all / Other**
  - Focus: Flexible, self-guided
  - Realistic? ○ Yes ○ No ○ Modify

**Question**: Are we missing any paths your participants need?

Answer: ___________________________________________________________

---

### A2: Question Difficulty & Ordering

**Current approach**:
- Start EASY (name, location) → confidence builder
- Then HARDER (describe work, achievements)
- Progressively more detailed

**For your participants:**

What's an EASY first question that builds confidence?
- [ ] Name, email, phone
- [ ] "Where are you from?"
- [ ] Other: _____________________

What's the HARDEST question they might freeze on?
- [ ] Describing tasks/responsibilities
- [ ] "What did you achieve?"
- [ ] Dates and timelines
- [ ] Other: _____________________

Should we ask them in different order based on path?
- [ ] Yes (customize per path)
- [ ] No (same order for all)

---

### A3: Language Handling

**What languages do your participants speak?**

- [ ] German only
- [ ] German + English
- [ ] German + English + [other]: _____________
- [ ] Very mixed (many languages)

**Input language**:
Should we accept input in:
- [ ] German only
- [ ] Any language (system normalizes to German)
- [ ] Multiple languages (show in dropdown)

**Output language**:
What languages should the final CV be available in?
- [ ] German only
- [ ] German + English
- [ ] Other: _____________

**Literacy challenges**:
Do any participants have:
- [ ] Limited German reading/writing
- [ ] Very basic literacy
- [ ] None of the above

If yes, what should we do differently? _________________________________

---

## B. EXAMPLES & GUIDANCE

### B1: Good/Bad Examples

**Current approach**: Every question shows 1 good example + 1 bad example

**Question**: Should examples be:
- [ ] Generic/neutral (OK for all jobs)
- [ ] Role-specific (customize per path)
- [ ] Real examples from your region's job market

**Where should examples come from?**
- [ ] We write them (generic)
- [ ] You provide real CVs from past students (anonymized)
- [ ] Job postings from your region

**Examples we need to define**:
- [ ] Examples for "unemployed" path
- [ ] Examples for "career switch" path
- [ ] Examples for "student" path
- [ ] Examples for "career pause" path
- [ ] Examples for "tools/systems" question
- [ ] Examples for "achievements" (if we ask it)

**Action**: Collect 2-3 good real CV samples per path → we'll extract examples

---

### B2: Quick-Fill Buttons

**Current approach**: Buttons like "I worked with machines", "I worked with customers"

**Question**: For your participants, what are common quick fills?

For EXPERIENCE:
- [ ] "I worked with machines"
- [ ] "I worked with people/customers"
- [ ] "I did office work"
- [ ] "I was a manager/supervisor"
- [ ] Other: ________________________________

For TOOLS:
- [ ] "Microsoft Office (Word, Excel)"
- [ ] "Hand tools, machinery"
- [ ] "Cash register, POS system"
- [ ] "Construction tools"
- [ ] Other: ________________________________

For SKILLS:
- [ ] "Customer service"
- [ ] "Team work"
- [ ] "Problem solving"
- [ ] "Leadership"
- [ ] Other: ________________________________

**Action**: Define 5-10 quick fills per category relevant to your region

---

## C. COMPLIANCE & STANDARDS

### C1: AMS Wording Requirements

**Does your AMS have rules about how CVs should be written?**

Forbidden or discouraged words:
- [ ] First person ("I", "me", "my") — forbidden everywhere
- [ ] Specific vague words: ___________________________
- [ ] Exaggeration words: ____________________________
- [ ] Other rules: _________________________________

Required format:
- [ ] Europass (EU standard) — yes, we use this
- [ ] Specific AMS format? ___________________________
- [ ] Font/size/color requirements? ___________________________

Required sections:
- [ ] Education — yes (locked)
- [ ] Experience — yes (locked)
- [ ] Skills — yes (locked)
- [ ] Languages — yes (locked)
- [ ] Certifications — important?
- [ ] Volunteer work — important?
- [ ] Cover letter — need this too?

---

### C2: Skills & Competencies

**What skills does AMS care about?**

Should we use:
- [ ] ESCO skill taxonomy (EU standard) — recommended
- [ ] Custom AMS skill list: ___________________________
- [ ] Whatever participant writes (no validation)

**Regional focus** — Any specific skills critical in your region?

Examples: Specific certifications, languages, tools, sectors
___________________________________________________________________

---

### C3: Certification/License Handling

**Should we ask about certifications?**

- [ ] Yes — very important for your participants
- [ ] No — they'll add if relevant
- [ ] Only for specific roles: ___________________________

**List certs we should recognize** (automatically highlight):
- [ ] Driver's license
- [ ] Forklift certification
- [ ] Safety certifications (which ones?): _______________
- [ ] Professional certs: _______________
- [ ] Language certs: _______________
- [ ] Other: _______________

---

## D. UX & TONE

### D1: Reassurance & Encouragement Level

How reassuring should the system be?

- [ ] Minimal — just factual
- [ ] Moderate — regular reassurance ("This is going well")
- [ ] High — very encouraging, frequent "You're doing great"

**For your participants**, which feels right? ______________________

---

### D2: Naming & Language

Words we should AVOID (scary, corporate, complex):
- [ ] "Achievement" (use: "What did you do well?")
- [ ] "Competency" (use: "Skill")
- [ ] "Comprehensive background" (use: "Tell us about your work")

Other words to avoid: ___________________________________________________

Words we should USE (encouraging, simple, human):
- [ ] "Tell us" (instead of "Provide")
- [ ] "Tell us what you did every day" (concrete, not abstract)
- [ ] "Did you help anyone?" (relatable)

Other good words/phrases: ___________________________________________________

---

### D3: Pacing & Pressure

Should the system feel:
- [ ] Fast-paced (get it done quickly)
- [ ] Relaxed (take your time, can come back)
- [ ] Very patient (lots of reassurance, can skip)

**For your participants**: Which approach? ______________________

---

## E. TRAINER WORKFLOW

### E1: How Will Trainers Use This?

**Review speed requirement**:
How much time should a trainer spend per participant?
- [ ] 2-3 min (quick approval only)
- [ ] 5-10 min (review + small edits)
- [ ] 15+ min (deep review + teaching)

**This affects UI design** — faster review = simpler interface.

---

### E2: Editing Authority

**What should trainers be able to edit?**
- [ ] Everything (full control)
- [ ] Specific fields only (which?): _______________
- [ ] Can't edit, only approve/reject

**What should be locked** (can't edit)?
- [ ] Nothing (trainer has full control)
- [ ] Certain sections (which?): _______________

---

### E3: Teaching Use

Will trainers use AMS JobAssist in class to teach?
- [ ] Yes — show before/after examples
- [ ] No — just CV generation tool
- [ ] Maybe — depends on trainer

If YES, how?
- [ ] Project on screen, teach class together
- [ ] Show individual students their before/after
- [ ] Use as homework review discussion

**This affects design** — if teaching, we need good before/after display.

---

### E4: Batch Operations

What batch operations matter?
- [ ] Export all approved CVs as PDF (high priority)
- [ ] Export as Word (editable)
- [ ] Bulk approve/reject
- [ ] Filter by completion status
- [ ] Generate records/reports

---

## F. TECHNICAL & ACCESSIBILITY

### F1: Computer Access

**Do your participants have:**
- [ ] Computer access at home (homework possible)
- [ ] Only access in class (in-class only approach)
- [ ] Limited/no home access (must run in-class)

**Internet availability**:
- [ ] Reliable internet (online systems OK)
- [ ] Unreliable (must work offline)
- [ ] No internet (must work completely offline)

---

### F2: Device Specs

Will system run on:
- [ ] Modern computers (2015+)
- [ ] Old computers (2010+)
- [ ] Very old Windows (Windows 7, even older?)

**This affects tool requirements** — older machines = lighter system.

---

### F3: Accessibility

Do participants have any of these needs?
- [ ] Vision/reading challenges (need bigger fonts, high contrast)
- [ ] Keyboard-only use (no mouse)
- [ ] Slow typing speed (auto-expand quick fills)
- [ ] Non-native German readers (simple language)

---

## G. SUCCESS CRITERIA

### G1: What's a "Good CV"?

For your AMS/region, what makes a CV good?

Checklist:
- [ ] Has all required sections (exp, education, skills)
- [ ] Professional language (no slang, proper grammar)
- [ ] Concrete details (not vague)
- [ ] Proper length (1-2 pages)
- [ ] Europass format (EU-standard)
- [ ] Region-specific format: _______________
- [ ] Includes certifications (if any)
- [ ] Other: _______________

---

### G2: Participant Success

How will you know if AMS JobAssist worked?

Measure (pick 2-3):
- [ ] Participants complete the interview (what %?)
- [ ] Trainers use it regularly (how often?)
- [ ] Quality of generated CVs is higher (how judge?)
- [ ] Participants feel more confident (survey?)
- [ ] Job placement improves (follow-up metric?)
- [ ] Other: _______________

---

## H. DATA & PRIVACY

### H1: Data Handling

Participants' data should:
- [ ] Stay on trainer's computer (most private)
- [ ] Never leave the AMS center (offline only)
- [ ] Be completely deleted after course (no archiving)
- [ ] Be kept for records (how long?)

**This affects storage design** — secure, private default.

---

### H2: Audit & Records

Should system track:
- [ ] Who approved each CV?
- [ ] When was it approved?
- [ ] What edits were made?

Why? ________________________________________________________________________

---

## I. ROLLOUT PLAN

### I1: Pilot Group

**First test with:**
- [ ] Full class (XX participants)
- [ ] Small group (5-10)
- [ ] Just trainers (internal test)

**Timeline**:
- [ ] Test date: _______________
- [ ] Feedback date: _______________
- [ ] Go-live date: _______________

---

### I2: Feedback & Iteration

**How will you gather feedback?**
- [ ] Survey participants
- [ ] Trainer interview
- [ ] Monitor usage data
- [ ] Check CV quality

**Feedback loop**:
- [ ] We build, you test, we refine
- [ ] Timeline: 4 weeks build → 1 week test → 1 week refine

---

## Summary: What You're Deciding

By filling this out, you're defining:

1. **Who it's for** — Which participants, their challenges, their goals
2. **What it teaches** — Interview paths, examples, skills, language
3. **How it's used** — In-class, homework, or blended
4. **How it looks** — Tone, pace, encouragement level
5. **What success looks like** — Quality criteria, completion rates
6. **How trainers work with it** — Fast review, teaching moments, batch export

---

## Next Steps

1. **Schedule kickoff call** with your AMS instructors
2. **Work through this checklist together** (2-3 hours, very important)
3. **Provide to development team** (we'll build based on your answers)
4. **Finalize examples & quick fills** (with real CVs from your region)
5. **Decide pilot date** (when do we test with real participants?)

---

## Questions?

This checklist defines the tool. The more specific your answers, the better AMS JobAssist will work for your participants.

**Don't skip this. This is the real work.** ✓

