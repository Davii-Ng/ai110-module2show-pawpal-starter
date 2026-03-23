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


VS Code Copilot was most helpful when used as a focused assistant for each step of the scheduler. The strongest features were inline completions for repetitive class logic, chat for debugging scheduler constraints, and quick suggestions for test cases tied to recurrence and conflict handling.

I used Copilot most effectively for converting ideas into clean, testable methods like sorting, filtering, and schedule generation. It helped speed up implementation, but I still verified behavior with tests and manual checks before accepting changes.

One suggestion I intentionally modified was using a more advanced optimization-based scheduler. I kept a greedy/first-fit design instead because it matched the assignment scope, stayed easier to explain in UML and reflection, and reduced complexity in both code and testing.

Using separate chat sessions for design, coding/debugging, and documentation kept the project organized. It prevented context overload, made prompts more specific, and helped me track which decisions were final versus still experimental.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment I did not accept an AI suggestion as-is was when it recommended moving toward a more advanced optimization-based scheduler. While that approach could potentially improve global scheduling quality, I decided not to adopt it for this project because it added too much complexity for the assignment scope.

I evaluated that suggestion by comparing it against my goals: clarity, testability, and alignment with the rubric. I verified my final decision by keeping the greedy/first-fit scheduler and running targeted tests for sorting, recurrence, conflict detection, and unscheduled-task reasons. Since those tests passed and the behavior was explainable in both UML and reflection, I kept the simpler design.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?


I tested both core model behavior and scheduler behavior. On the model side, I verified that marking a task complete updates state correctly and that adding a task to a pet updates the pet’s task list. On the scheduler side, I tested chronological sorting, daily recurrence creation (completing a daily task creates the next day’s task), conflict detection for overlapping times, and edge conditions such as no tasks, tasks outside the day window, and tasks that miss latest_time

These tests were important because they validate the most failure-prone parts of the system: time ordering, recurrence logic, and schedule feasibility. If these behaviors are wrong, the generated plan can become confusing or unsafe for real pet care routines.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am moderately high in confidence (about 4/5) that the scheduler works correctly for normal daily planning scenarios. The current tests cover both happy paths and key edge cases, and the app surfaces unscheduled reasons and conflict warnings clearly, which makes behavior easier to verify.

If I had more time, I would add tests for larger mixed-priority task sets, more complex recurring patterns over multiple days, and tighter validation of owner-availability constraints. I would also test robustness against malformed user inputs and stress-test scheduling with many overlapping tasks to measure consistency and performance.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part I am most satisfied with is turning an initial UML idea into a working system with clear behavior and explainable outputs. I am especially happy with how the scheduler handles practical constraints like time windows, recurrence, and conflict warnings while still staying simple enough to test and present clearly in the UI.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would like to have a clearler and cleaner design.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?


One important thing I learned is that system design is iterative: initial UML is a useful starting point, but implementation and testing reveal what must change. I also learned that AI tools are most effective when used critically, with clear prompts and verification through tests, rather than accepting suggestions without evaluation.