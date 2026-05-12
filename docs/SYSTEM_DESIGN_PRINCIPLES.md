# AMS JobAssist — System Design Principles

**Foundation**: Tested principles from similar systems designed for vulnerable populations and low-confidence users.

---

## 1. CONVERSATIONAL QUESTIONING (Not Forms)

### Principle
Replace forms with adaptive conversational questioning. Progressive depth — start shallow, go deeper only when the user is engaged.

### Applied to AMS JobAssist

**Hierarchy of Input Methods:**
1. **Conversation** (default, always) — "Tell us about your last job"
2. **Micro-prompts** (when needed) — "Did you use tools?" / "Did you work with people?"
3. **Structured input** (optional, never forced) — Text field for details

**Never ask:** "Describe your professional background and key responsibilities"  
**Always ask:** "What did you do at your last job? You can write a few words or sentences."

### Implementation
- Questions appear one per screen
- Each question has a clear, conversational tone
- Users can answer in their own words (any language)
- Follow-up questions are specific, not open ("Did you use machines?" vs "Tell me more")

---

## 2. LOW-EFFORT INPUT BY DESIGN

### Principle
Never ask for what you can infer. Design for minimum cognitive load at every step.

### Applied to AMS JobAssist

**Quick-Fill Buttons** reduce generation burden:
- "I worked with machines"
- "I worked with customers"
- "I did office work"
- "I managed people"

Users select rather than create. Selection is infinitely easier than generation.

**Never ask the user to generate what can be structured:**
```
❌ "Describe your skills"
✅ "Did you use Microsoft Office, hand tools, or machines?"
```

**Clarification Layer** — When answer is unclear or too short:
```
❌ "Can you tell me more?"
✅ "What tools or machines did you use?"
✅ "Did you work with other people or mostly alone?"
✅ "Was this inside (office/warehouse) or outside?"
```

Specific questions, not open ones. Always offer a choice.

### Implementation
- Pre-written quick-fill options for every question
- Specific follow-up questions, never "tell me more"
- Allow short answers — system improves them, doesn't block them
- Remove decisions where possible — tell user where to start, not ask

---

## 3. NO FAKE REASSURANCE

### Principle
Don't give empty "great job!" responses. Explain mechanisms clearly. Always show that progress is happening.

### Applied to AMS JobAssist

**Wrong:** "Great answer! ✓"  
**Right:** (after showing improved version) "See how we made this more specific? Instead of 'office work', we said exactly what tools and tasks. That's what employers look for."

### Every Output Must Have Four Parts

1. **Observation** — what was noted
   - "You said: 'worked with wood'"

2. **Mechanism** — why it matters
   - "That tells us: manual fabrication, tool operation, physical workflow"

3. **Implication** — what it means for the user
   - "What it means: you have skilled trade experience — that's valuable"

4. **Next Step** — exactly what to do now
   - "Your CV now says: 'Holzbearbeitung, Maschinenbedienung, manuelle Fertigung'"

### Implementation
- Every transformation shows: original → improved + explanation
- Progress bar is factual (Step 3 of 8), not motivational
- "Saved ✓" confirms action, doesn't celebrate
- Feedback is specific, not generic

---

## 4. TASK INITIATION PARALYSIS (The Blank Page Problem)

### Principle
The hardest part is the first 30 seconds. Remove that barrier.

### Applied to AMS JobAssist

**2-Minute Commitment Strategy:**
"Just answer this one question. You can stop after." → User almost never stops.

**Tiny Win First:**
First question must be answerable immediately (name, city, location). Completion → dopamine → easier to continue.

**Remove First Decision:**
Don't ask "where do you want to start?" Tell them: "Let's start with your name."

**Pre-Written Starter Options:**
Every question has quick-fill buttons to avoid blank page.

### Implementation
- First 2 questions (name, location) are trivial wins
- Every question has example buttons ready to select
- Progress bar shows completion immediately
- No blank text field ever — always suggest starting options

---

## 5. EXECUTIVE DYSFUNCTION & WORKING MEMORY FAILURE

### Principle
If it is not written down and visible, it does not exist for the brain under cognitive load.

### Applied to AMS JobAssist

**Visibility Requirements:**
- **Progress bar** — non-negotiable, shows exactly where in interview
- **"Saved ✓"** indicator — confirms progress was not lost
- **Auto-resume** — exact question they left on, every time
- **Summary available** — "Here's what you've told us so far"

**Never require the user to remember:**
- What they said on a previous screen
- Where they are in the process
- How much is left to do
- That their data was saved

### Implementation
- Progress bar on every screen: "Question 3 of 12"
- "Saved ✓" visible after every answer
- Autosave to persistent storage (SQLite)
- Session resume shows last question completed
- Summary screen available at any point

---

## 6. OVERWHELM = SYSTEM SHUTDOWN

### Principle
When cognitive or sensory load hits critical, executive function collapses. The only fix is reduction.

### Applied to AMS JobAssist

**One Thing Per Screen**
- One question only
- Maximum two input fields
- Maximum one concept per question
- Short sentences, not paragraphs

This is not a UX preference. It is a hard technical requirement.

**Sensory Load Reduction:**
- Plain text, no heavy design
- Consistent simple layout
- No animations or transitions
- No color coding (simple ✅/⚠️/❌ only)
- Readable font size (minimum 14pt)
- Lots of white space

### Implementation
- Never two questions on one screen
- Never more than 2 inputs per screen
- Minimum sensory complexity
- Consistent layout every screen
- Easy skip: [Back] [Skip for Now] [Next] always available

---

## 7. SHAME AMPLIFIES PARALYSIS

### Principle
The shame cycle: don't do it → feel bad → can't start → feel worse → can't start.

Breaking the cycle requires showing that effort is noted and improvement happens automatically.

### Applied to AMS JobAssist

**The Re-Ask Must Never Feel Like Failure:**

```
❌ "That answer is too short."
✅ "Can you tell us a bit more? For example, what tools did you use?"
```

**Show Transformation Without Judgment:**

```
User wrote: "I worked in a store"
System shows: "Here's what we made of that:
              Retail Associate — managed inventory, 
              customer service, sales transactions"
```

Not: "You said this poorly, we fixed it."  
But: "You gave us the raw material, we polished it."

**Never Use These Words:**
- insufficient
- weak
- poor
- bad
- incomplete
- inadequate
- failure

**Always Use:**
- "Let's add more detail"
- "Can you tell us a bit more?"
- "What else can you remember?"
- "That's a great start"

### Implementation
- Re-ask tone: curious, not corrective
- Show improvement as system skill, not user failure
- Celebrate completion of each section
- Validate before asking for more
- No quality scoring shown as red/bad

---

## 8. REAL-TIME ADAPTATION BASED ON OBSERVED PATTERN

### Principle
Different users have different communication styles. Adapt in real-time based on what you observe.

### Applied to AMS JobAssist

**Observed Signal → Adaptation:**

| Signal | Adaptation |
|--------|-----------|
| Very short answers (< 10 words) | Offer more quick-fill buttons, shorter questions |
| Long structured answers | Reduce examples, give more open questions |
| Non-German words mixed in | Increase language reassurance, keep examples in German |
| Multiple answers to different Qs are identical | Flag for trainer review, move on with placeholder |
| Fast completion | User is comfortable — reduce reassurance, increase pace |
| Slow pace between answers | User may be struggling — add more examples, more buttons |
| Sudden abandonment after specific Q | That question may be too hard or triggering — flag for trainer |
| Multiple skipped questions in a row | User overwhelmed — reduce options, simplify next Q |

### Implementation
- Track answer length and complexity per answer
- Adjust next question based on observed pattern
- Flag suspicious patterns for trainer attention (identical answers, abandonment)
- Trainer gets alert: "This participant may have misunderstood Q7 — check this one"

---

## 9. THREE-PART EMPATHY MODEL FOR COPY

### Principle
Every interaction should hit three levels: cognitive empathy, affective empathy, compassionate action.

### Applied to AMS JobAssist

**Three Parts Every Interaction Should Have:**

1. **Cognitive Empathy** — understand the user's experience
   - "This part can feel difficult"
   - "Many people find this hard to describe"

2. **Affective Empathy** — reflect feeling appropriately
   - "That sounds frustrating"
   - "It's normal if you're not sure"

3. **Compassionate Action** — move them forward
   - "Here's an example to get you started"
   - "Let's try a different angle"

### Example: When User Gets Stuck

```
User struggles with question about achievements.

❌ Wrong: "What were your achievements?"

✅ Right:
"Many people find this part hard because 'achievement' sounds big.
But it's not — it just means: something you did, or something 
that went well.

For example:
✓ 'I finished a project on time'
✓ 'I helped a customer find what they needed'
✓ 'I learned to use a new tool'

What's something like that from your experience?"
```

### Implementation
- Every question that might trigger shame has validation copy first
- Copy acknowledges difficulty, then normalizes it, then offers concrete example
- Tone is warm but not therapeutic — this is not counseling
- Boundaries on empathy support — validate, don't over-help

---

## 10. LEARNING PROGRESSION: CONCRETE → ABSTRACT

### Principle
Start with what users can already say. Build from concrete to abstract. The tool does the abstraction, not the user.

### Applied to AMS JobAssist

**Progression in a Single Question:**

```
Step 1 (Concrete): "What did you do every day at that job?"
User says: "I helped old people wash and eat"

Step 2 (Specificity): "Did you do this every day? Was it one person or many?"
User says: "Every day, usually 5-6 people"

Step 3 (Abstraction - Done by System): Output becomes:
"Betreuung von pflegebedürftigen Personen, Unterstützung 
bei der Körperpflege und Mahlzeiteneinnahme, tägliche 
Assistenzleistungen für 5-6 Personen"
```

User never has to do the abstraction. Tool does it.

**Progression Across Entire Interview:**

1. **Concrete daily tasks** — "What did you do every day?"
2. **Specific task details** — "What tools?" "Who did you work with?"
3. **Abstract skill labels** — System generates these
4. **Professional CV language** — System generates this

### Implementation
- Questions start with "what did you do" not "what skills do you have"
- Follow-up questions ask specific details, not concepts
- System maps details → skills → CV language
- User never sees the abstraction step, only the input and output

---

## 11. IMMEDIATE REWARD LOOPS

### Principle
Dopamine-driven learning — the reward must be immediate, not deferred.

### Applied to AMS JobAssist

**Rewards at Every Step:**

| Action | Reward |
|--------|--------|
| Answer question | Progress bar moves, "Saved ✓" appears |
| Complete section | Summary shows what's been built |
| See live preview | CV showing updated content |
| Finish interview | Full CV ready to download |
| Each step | Small visible progress |

**Never:**
- Make user wait for results
- Hide progress ("processing...")
- Require completion of whole section before showing benefit
- Defer feedback

### Implementation
- Progress bar increments after every single answer
- "Saved ✓" appears instantly
- Live preview updates in real-time
- Section completion celebrated immediately
- Results always instant (no loading screens)

---

## 12. NO "PREREQUISITE TRAP"

### Principle
Don't block progress because a section is incomplete. Allow skip and come back. Partial CV is better than abandoned CV.

### Applied to AMS JobAssist

**Every Question Has Three Buttons:**
- [Back] — go to previous question
- [Skip for Now] — come back later
- [Next] — continue

**No Mandatory Fields** (except name)
User can skip education, skip certifications, skip languages. CV still generates.

**Resume from Exact Point**
User can stop mid-interview, close browser, come back tomorrow. Resumes on exact question they left on.

### Implementation
- Skip button on every question
- No validation blocking next step (except quality: < 5 words re-asks)
- Auto-save means user never loses progress
- Session resume on exact question
- CV generates with available data only

---

## 13. AGE-STAGE AWARENESS

### Principle
AMS participants span 18–60+. Cognitive needs, stress responses, and learning styles differ by life stage.

### Applied to AMS JobAssist

**Young Adults (18–25):**
- Still forming professional identity
- High shame sensitivity
- Shorter sessions work better
- **Adaptation:** More reassurance, examples from peers their age, shorter pacing

**Prime Working Age (25–45):**
- Career switching or re-entering
- Often poor vocabulary for describing work (tradespeople, caregivers)
- Underreport — "I just did my job"
- **Adaptation:** Concrete task questions ("what at 9am?"), specific clarification, phrase to show value

**Older Adults (45–60+):**
- May have literacy/tech difficulty
- Long career = cognitive load
- More formal self-presentation
- **Adaptation:** Longer screens OK, fewer sections required, more reassurance on tech

### Implementation
- Pre-gate captures both situation AND inferred age-stage from writing pattern
- Pacing adjusts by age (18–25: faster, 45–60: slower)
- Examples adjust by age (peer examples for young, experienced examples for older)
- Required sections adjust (older users can skip less relevant sections)

---

## 14. VALIDATION-FIRST-FIX-LATER

### Principle
Before fixing or asking for more, validate that you understood.

### Applied to AMS JobAssist

**Every Re-Ask Follows This Pattern:**

1. **Show what you understood**
   - "So you worked in construction"
   - "You said you managed a team"

2. **Validate it**
   - "That's valuable experience"
   - "That shows leadership"

3. **Ask for clarification**
   - "Can you tell us what you actually did every day?"
   - "What was the main task?"

```
❌ Wrong:
"That answer is too vague."

✅ Right:
"You mentioned construction work — that's good.
Can you tell us what you actually did every day?
For example: mixing concrete, operating equipment, managing the site?"
```

### Implementation
- Every response reflects back what was understood
- Validation comes before request for more
- Specific follow-up questions, not generic re-asks
- Tone shows: "I understood, now help me understand more"

---

## 15. SAFETY ESCALATION MODEL

### Principle
Some participants may be in distress. The interview should detect escalation signals and have a soft exit.

### Applied to AMS JobAssist

**Escalation Signals (Flag for Trainer):**
- Sudden abandonement mid-interview
- Multiple questions about same topic without progress
- Answers indicating trauma or crisis ("I don't deserve a job")
- Rapid deterioration in answer quality
- Explicit statements of distress

**Soft Exit (Not Forced Completion):**
- User can skip any question
- User can stop at any time
- If pattern suggests crisis → system suggests "save progress and take a break"
- Trainer gets alert with transcript for follow-up

### Implementation
- Track completion pattern for sudden drops
- Flag any answers with crisis keywords
- Offer natural pause points ("You've done great. Want to take a break?")
- Trainer gets summary of any escalation signals before review

---

## 16. UNCERTAINTY TRACKING

### Principle
When system is unsure, flag it for trainer. Never present machine output as certain when it isn't.

### Applied to AMS JobAssist

**When to Flag:**
- Unclear answer that system couldn't parse
- Ambiguous skill normalization (multiple possible interpretations)
- Duplicate answers to different questions
- Answer pattern that doesn't match question
- Missing key information (no job title, no dates, no company)

**Trainer Gets:**
- Original text highlighted in yellow
- Question flag: "Unclear — check with participant"
- System's best guess shown
- Trainer final decision on what goes in CV

### Implementation
- Uncertainty scoring on every polished answer
- Trainer dashboard flags > 50% uncertainty
- Comments like "Please clarify job title with participant"
- Trainer always has final say on flagged items

---

## Summary: How These Principles Work Together

```
START:
Conversational gate (not forms) → captures situation

INTERVIEW:
One question per screen (no overwhelm)
+ quick-fill buttons (low effort)
+ specific examples (not blank page)
+ immediate "Saved ✓" (working memory)
+ easy skip (not trapped)

REAL-TIME:
Observe answer length → adapt next question
Flag misunderstandings → trainer alert
Track shame signals → adjust tone

OUTPUT:
Show transformation (observation→mechanism→implication→next)
+ no fake reassurance
+ validation before fix
+ concrete→abstract (tool does it)

LEARNING:
Immediate rewards (progress bar)
+ dopamine on every step
+ resume from exact point
+ partial CV better than abandoned

AGE-AWARE:
Pacing by age stage
+ examples by age
+ reassurance level by age

RESULT:
User feels: guided, safe, accomplished
Trainer sees: clear before/after + flags
CV emerges: professional, complete, valuable
```

---

**These 16 principles are the foundation of every design decision in AMS JobAssist.**

If a feature or interaction violates one of these, redesign it.

