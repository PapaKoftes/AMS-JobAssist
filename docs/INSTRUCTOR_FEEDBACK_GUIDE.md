# AMS JobAssist: Instructor Feedback & Viability Review

**For**: Your Instructor/Advisor  
**Purpose**: Strategic feedback on product viability, usability, and real-world effectiveness  
**Time to review**: 30-45 minutes  
**Expected output**: Your actionable feedback to improve this product

---

## What Are We Building?

### The Vision (One Sentence)
A standalone CV-building tool that incorporates AMS training insights—designed so it works for anyone, but purpose-built from real employment training experience.

### The Two-Tool Strategy

**Tool 1: CV Maker** (Customer-Facing)
- Anyone can use it (job seekers, career changers, students)
- Guided interview based on AMS learnings
- Generates professional CV (PDF/DOCX/Europass)
- Works completely offline
- Downloadable export (JSON) for optional trainer use

**Tool 2: Trainer Dashboard** (Optional Addon)
- For AMS trainers managing cohorts
- Imports participant data from Tool 1
- Tracks progress, provides feedback, batch exports
- Only trainers use this—not required for Tool 1 to work

### Why This Two-Tool Model?

**Problem**: AMS training insights (how to write for nervous people, what questions work, how to build confidence) shouldn't be locked in an AMS-only tool.

**Solution**: Build the insights INTO the CV tool itself (Tool 1), so it works for anyone. Optional trainer management tool (Tool 2) lets AMS centers scale their use.

---

## Current Architecture

### What We Know (Locked Decisions)

✅ **Technology**:
- Backend: FastAPI (Python)
- Database: SQLite (offline-first, portable)
- Frontend: Vanilla JavaScript (no build complexity)
- AI: Ollama (local polishing only)
- Export: PDF, DOCX, Europass XML

✅ **Interview Design** (5 Hardcoded Paths):
1. Career switcher (recent job + new direction)
2. Unemployed/first-time jobseeker (education + skills)
3. Student/recent graduate (education + projects)
4. Career pause returner (last job + gap + direction)
5. Catch-all/flexible (self-guided)

✅ **16 UX Principles** (from AMS research):
- One question per screen (not overwhelming)
- Good/bad examples for every question (shows what works)
- Quick-fill buttons (saves typing for common answers)
- Auto-save every step (never lose progress)
- Live preview (see rough → polished in real-time)
- Gentle language (never say "weak" or "insufficient")
- Start easy, escalate gradually (confidence building)
- Re-ask on vague answers (minimum quality threshold)
- And 8 more...

✅ **Timeline**: 8 weeks total
- Weeks 1-4: Tool 1 (interview engine, polish, UI, testing)
- Weeks 5-8: Tool 2 (dashboard, import, reporting)

---

## Critical Questions for Your Feedback

### SECTION A: Product-Market Fit

**A1: Who's the Real Customer?**

*Our assumption:*
- Primary: Job seekers (any skill level)
- Secondary: AMS participants (with trainer support)
- Tertiary: Career coaches

**Your input:**
- Is this the right customer hierarchy?
- Which segment will actually USE this?
- Who has the pain point we're solving?
- Are we missing a critical customer type?

**A2: What's the Actual Problem?**

*Our assumption:*
- "People feel insecure about describing their work experience"
- "Writing a CV is intimidating for non-native speakers"

**Your questions:**
- Is this the REAL problem, or the symptom?
- What's the root cause of CV anxiety?
- Do people need a CV tool, or something else first?

**A3: Why Choose This Over Alternatives?**

*Alternatives:*
- LinkedIn (free), Canva (free), ChatGPT (free), hiring a coach ($)

**Your questions:**
- What does THIS tool do that others don't?
- Is "AMS-informed design" a real differentiator?
- Who would actually CHOOSE this over free tools?
- What's the compelling reason to use this?

**A4: Pricing & Money**

*Our assumption:*
- Tool 1: FREE (build audience)
- Tool 2: Could be free or paid

**Your questions:**
- Can a free tool sustain?
- Should trainers pay for Tool 2?
- Who's actually the paying customer?

---

### SECTION B: Usability & UX

**B1: Is the Interview Actually Good?**

*What we designed:*
- 5 interview paths
- One question per screen
- Good/bad examples for every question

**Your questions:**
- Do these 5 paths cover YOUR participants?
- Are question sequences right?
- Which questions cause people to freeze?
- Where do people abandon the interview?
- What makes people give up?

**B2: Will People Actually Finish It?**

*Our goal:*
- "Nervous person completes in 30-60 min and feels confident"

**Your questions:**
- Is 30-60 minutes realistic?
- Where do people drop out?
- What's the MINIMUM viable CV you need?
- Should we offer "express" vs "detailed"?
- How do we keep momentum if someone returns later?

**B3: Are Examples Actually Helpful?**

*Our design:*
- Every question shows good example + bad example

**Your questions:**
- Do examples match YOUR participants?
- Should examples be more diverse?
- Are "bad examples" recognizable as bad?
- Should we show REAL CVs from your region?
- Do examples need video, or just text?

**B4: Language & Tone**

*Our approach:*
- "Safe, encouraging" language
- Clear, not corporate

**Your questions:**
- Is the tone actually encouraging, or patronizing?
- For non-native German speakers, is the level right?
- Should interview be in multiple languages?
- Are there words that make people uncomfortable?
- Does it feel like a real person, or a robot?

**B5: The Auto-Improvement**

*Our design:*
- Tool auto-improves rough answers to professional language
- User sees before/after

**Your questions:**
- Do people TRUST the auto-improvement?
- Or does it feel like it's changing their story?
- Should people be able to edit/reject?
- Does this teach them to write better, or hide weakness?

---

### SECTION C: AMS Viability

**C1: Is Tool 1 "Purpose-Built for AMS"?**

*Our claim:*
- Incorporated 16 UX principles from AMS research

**Your questions:**
- Do these principles actually address YOUR needs?
- Are we missing critical AMS requirements?
- What does "AMS-appropriate" actually mean?
- Do Europass requirements match your rules?
- What compliance issues haven't we considered?

**C2: Will Trainers Actually Use Tool 2?**

*Our design:*
- Tool 2: Import participant data, track progress, batch export

**Your questions:**
- Do trainers WANT a tracking tool, or is it extra work?
- What reports matter most?
- Should Tool 2 integrate with your existing systems?
- How much time should Tool 2 take per participant?
- What do trainers actually need to see?

**C3: Will Tool 1 Replace Manual Review?**

*Our goal:*
- Participants use Tool 1 alone, trainers optionally use Tool 2

**Your questions:**
- Can trainers rely on Tool 1 output, or do CVs need heavy editing?
- What % of Tool 1 CVs are "trainable-ready"?
- Are there job types where Tool 1 just doesn't work?
- Should trainers still teach CV writing, or is Tool 1 the teaching?
- Does this replace trainer expertise, or enhance it?

**C4: Data & Privacy**

*Our design:*
- All data stays local (no cloud)
- Optional Tool 2 can be on AMS servers

**Your questions:**
- Is "no cloud" actually required?
- Should we allow Cloud backup?
- What privacy/GDPR rules apply?
- Who owns the CV once generated?
- Should data be encrypted?

---

### SECTION D: Technical Viability

**D1: Offline-First Design**

*Our approach:*
- Works completely without internet

**Your questions:**
- Is offline-only required?
- Would online+offline hybrid be better?
- What happens if someone wants syncing?

**D2: Deployment**

*Our plan:*
- Windows .exe (one file, double-click)
- Works on Windows 7+

**Your questions:**
- Is Windows-only OK?
- Is .exe the right distribution?
- Can it run on old computers?
- Should trainers run on servers or locally?

**D3: Updates After Release**

*Our concern:*
- How do we push updates (new questions, bug fixes)?

**Your questions:**
- Do users need automatic updates?
- Can trainers manage updates themselves?
- How do we add new interview paths after launch?

**D4: The AI Component**

*Our design:*
- Ollama (local, private) for language polishing
- Fallback if it fails

**Your questions:**
- Is local AI a real requirement?
- Could we use ChatGPT instead?
- Does "local AI" matter to users?
- What if Ollama fails?

---

### SECTION E: Viability & Scale

**E1: MVP vs Full Product**

*Our plan:*
- 8 weeks for both tools

**Your questions:**
- What's MINIMUM viable? (1 tool? 1 path?)
- Should we launch Tool 1 first, then Tool 2?
- Can we get to market faster with less?

**E2: Distribution & Growth**

*Unknown:*
- How do people find this?
- How does it spread?

**Your questions:**
- Is this AMS-specific or mass market?
- Do we need marketing?
- What's the go-to-market strategy?
- Should we target AMS first, then scale?

**E3: Long-Term Sustainability**

*Concern:*
- How do we keep this alive?
- Who pays after 8 weeks?

**Your questions:**
- What's the cost to maintain?
- Is this a one-time project or ongoing?
- Should we build a company around this?

**E4: Competitive Threat**

*Risk:*
- What if Google/Canva builds this?

**Your questions:**
- What's our defensible advantage?
- Is there first-mover advantage?
- Should we move faster?

---

### SECTION F: The Hard Questions

**F1: Is This Actually Solving an AMS Problem?**

*Real talk:*
- Do trainers think "we need a CV tool"?
- Or do they think something else?
- Is CV writing the bottleneck, or something before/after?
- What would trainers actually PAY for?

**F2: Are We Over-Engineering?**

*Honesty check:*
- Is the 16 UX principles too complex?
- Would a simpler form work just as well?
- What's the ACTUAL minimum that helps?

**F3: Is the "AMS-Informed" Angle Real?**

*Truth test:*
- Would this work just as well without "AMS"?
- Are we solving AMS problems or just building a CV tool?
- Should we market to AMS or job seekers?

**F4: What Are We Missing?**

*Blindspots:*
- What problems aren't we seeing?
- What would make trainers choose this?
- What would make job seekers recommend it?

---

## What We Need From You

### 1. Feasibility
- Is this buildable in 8 weeks?
- Missing technical challenges?
- Is timeline realistic?

### 2. Viability
- Will anyone actually use this?
- Is there real demand?
- Path to sustainability?

### 3. Strategic Direction
- Should we pivot?
- Best go-to-market approach?
- Who's the real customer?

### 4. Usability
- Will the interview work?
- Where will people struggle?
- What would make it better?

### 5. AMS Specific
- Does this help YOUR AMS?
- What would trainers value?
- What are we missing?

---

## How to Use This Document

**Option 1: Written Feedback**
- Read, make notes, send back with comments

**Option 2: Conversation**
- Pick 3-4 sections that matter most
- Discuss in detail
- We iterate

**Option 3: Workshop**
- Go through with your team
- Collect multiple perspectives
- Identify priorities

---

## The Bottom Line

Before we code Week 1, we need clarity on:

1. **Who's the customer?** (Job seekers? Trainers? Both?)
2. **What's the ONE thing this does better?**
3. **Will anyone actually use/pay for this?**
4. **Is AMS the right focus?**
5. **What's the minimum viable product?**
6. **How does this reach customers?**

Your honest feedback now saves weeks of building the wrong thing.

---

**Goal**: Build something people actually want and use. Not something technically impressive. Not a "nice to have." Something that solves a real problem so well that people choose it.

That's viability.

**Your feedback shapes this product. Be honest.**
