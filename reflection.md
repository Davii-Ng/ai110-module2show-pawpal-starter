# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

There would be a total of four main class: Owner, Pet, Task. Scheduler

class Owner:
- personal information such as Name, Phone Number, Email
- Pets names
- Avalibility

the Owner could have 1 or many pets

class Pet:
- Name
- Type of animal
- Upcoming tasks
- Current tasks
- Pickup time

A pet can have multiple tasks

class Task:
- Type of task (walks, feeding, meds, enrichment, grooming, etc.)
- Task duration
- Pet assign
- Priority
- Task price

A pet would have a schedule that contains many tasks

class Schedule:
- Task priority
- Tasks 
- Pet information 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

- Copilot indentifies that there are no ID management system, which may cause collision upon creating an object.q

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler accounts for constraints such as task time windows (earliest and latest times within a day), task duration, provider availability to prevent overlapping assignments, task priority, pet assignment, and recurrence or completion status. Hard constraints—like time windows and provider availability—are enforced first to ensure tasks are feasible. 

When conflicts arise among feasible tasks, priority determines the order of scheduling. Soft preferences, including owner availability and pet-specific needs, are considered afterward. This approach keeps the system simple, predictable, and effective for small-to-medium workloads.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- Tradeoff: the scheduler uses a simple greedy/first-fit approach instead of an optimal global solver.

- Why reasonable: greedy is fast and easy to implement, and it gives good enough schedules for small teams and typical daily workloads without heavy computation.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
