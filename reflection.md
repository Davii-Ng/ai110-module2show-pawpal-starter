# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?


My initial UML had four main classes: Owner, Pet, Task, and Scheduler.

Owner: stores owner profile info (name, phone, email), availability, and pet references.
Pet: stores pet profile info (name, species, notes, pickup context) and associated tasks.
Task: stores task details (type, duration, priority, cost, pet assignment, time constraints).
Scheduler: generates a daily plan from tasks and constraints.
Relationship assumptions:

One owner can have many pets.
One pet can have many tasks.
A schedule is produced from tasks and constraints rather than manually entered.

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

A major tradeoff is using a greedy/first-fit strategy instead of a global optimization solver.

Why this is reasonable:

It is simple to implement and explain.
Runtime is fast for small to medium workloads.
It gives stable “good enough” results for the assignment scope.
Limitation:

Greedy decisions are local, so it can miss a globally better arrangement that would schedule more high-priority tasks.

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
