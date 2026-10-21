# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
The initial design revolved around 4 different classes: The owner, pet, scheduler, and tasks. These were the baseline classes that interacted with each other throughout the application lifecycle. I asked claude to ensure those were viable classes that would interact with each other as well to make sure each method that is performed in each class makes sense like owner adding a pet to establish a relationship for the scheduler.
- What classes did you include, and what responsibilities did you assign to each?
I included the classes of owner, pet, scheduler, and tasks. The owner primarily has a relationship with the pet and the scheduler, and they have the primary responsibility of adding pets, establishing preferences for suggestions the assistance takes into account for the scheduler, and availability. The pet has the primary responsibility of holding which tasks is added/removed and loading unfinished tasks. The task class hosts responsibilities for the priority of a task created, whether that task was completed, and time constaints for when a task needs to be completed. The scheduler is the one with the most responsibilities as it combines all the other classes to filter, hold all tasks, detect conflicts, build the plan, and explain the plan to the user.

**b. Design changes**

- Did your design change during implementation?
No. I felt the changes made might not be viable as this is a file that will get referenced in the main python file so many suggestions were made with the location of each method. At the moment, I will not implement the changes suggested unless otherwise needed.
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
It takes into account the priority, times, preferences, the pet the task is set for, and estimated time to complete with the actual time that the task was considered to do constraints

- How did you decide which constraints mattered most?


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The scheduler has the tradeoff that each scheduled time is fixed with no other suggestion for the time to do that task. This could be due to non specified constraints too such as leaving the house for other tasks like work, errands, or personal time.

- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable as it keeps a precise schedule in order to help. If the constraints were not updated to take into account external factors that could change the times, it is reasonable to assume outside forces might not interfere with the proposed schedule.

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
