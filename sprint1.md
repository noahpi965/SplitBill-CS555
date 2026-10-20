This sprint introduces you to Agile teamwork. You will take your team’s user stories and deliver a first working increment of your app. The focus is not on building everything at once but on experiencing the Agile process: planning, dividing work, building features, and reviewing progress.

Precondition: Sprint 1 Planning (from Activity 4)
Before starting this sprint, your team should have already:

Defined a Sprint Goal

Selected one user story per team member

Estimated effort (story points)

Set up your repository and project board

You will now execute the sprint based on that plan.

🔒 Sprint Freeze
Once the sprint starts, you must not add, remove, or significantly change user stories within this sprint.
This practice, called sprint freeze, ensures stability and commitment to the sprint goal.

Sprint 1 Expectations
Backlog & Board Maintenance
Maintain your Kanban board (GitHub Projects, Trello, or Jira Free) with columns such as
To Do / In Progress / Review / Done.

Each user story should appear as a card linked to its GitHub branch (each member works on their own branch) or Pull Request (PR).

Keep the board current to reflect real-time progress throughout the sprint.

Development
Each team member must implement the user story assigned to them during Sprint Planning (Activity 4).
All development work should follow standard Agile and GitHub practices to ensure code quality, traceability, and smooth collaboration.

1. Branching and Commit Practices
Create a separate Git branch for your user story to avoid merge conflicts.

Example branch names: feature/login-page, feature/profile-edit, bugfix/api-error.

Make frequent, meaningful commits describing your work clearly (e.g., “Implement login form validation”).

2. Implementation
Implement the functionality required by your user story as defined in the Sprint 1 plan.

Keep your implementation focused on the story scope (don’t add unrelated features).

Follow good coding conventions and ensure your code is well-documented and readable.

3. Testing
For each user story, include at least one automated test case (unit or integration).

The test should verify a core function or acceptance criterion of your story.

Confirm that your tests pass locally before creating a Pull Request.

4. Pull Requests and Code Reviews
When your story implementation and tests are complete:

Open a Pull Request (PR) to merge your branch into the main branch.

Include a brief PR description (what was implemented and any known issues).

Every PR must be reviewed and approved by at least one teammate before merging.

GitHub provides a built-in function to assign reviewers and record approvals.

Resolve any comments or requested changes before merging.

CI/CD Setup (Basic)
Ensure all PRs trigger your CI pipeline (build, lint, and/or test).

Only merge branches after all CI checks pass.

Keep your build-status badge visible in the README to reflect the current state of your project.

Sprint Review (In-Class)
Show your working increment (demo your implemented features).

Each team member must demonstrate the user story they worked on.

Sprint Retrospective (Team Reflection)
As a team, document:

What went well

What didn’t

What to improve next sprint

Sprint 1 Deliverables Checklist
Each team must submit:

In-Class Demonstration

Demonstrate your working increment.

Each member shows the story they implemented.

PDF Report of Sprint 1
Filename: TeamName_Sprint1.pdf
(One submission per team through Canvas by ScrumMaster)

PDF Report Content Checklist
1. Story Board
URL to your Kanban board (GitHub Projects / Trello / Jira Free)

Screenshot of the board at the end of Sprint 1
(Columns should show To Do / In Progress / Review / Done)

2. Pull Requests (PRs)
One PR per user story

Table or list of PR URLs

Screenshot of each PR page showing:

Description of changes

Reviewer’s approval (✔ Approved)

CI check results (all passed)

3. Story Implementation Summary Table
Story ID / Name	Owner	Source File Location	Test Case Name / Location	Status (Done / In Progress / Blocked)
Example: US-01 Login	Alice	src/components/LoginForm.js	tests/loginForm.test.js	Done
Each story listed (one per individual)

Status clearly marked

At least one test case linked for each story

4. CI/CD Evidence
Screenshot of successful CI/CD run (GitHub Actions or equivalent)

Screenshot of build-status badge visible in README

Note describing what the pipeline currently runs (build / lint / test)

5. Team Reflection (Sprint Retrospective)
Brief team reflection (≈ ½ page):

What went well

What did not go so well

What the team will change or improve next sprint

Each team member adds a 1–2 sentence personal contribution summary

6. Sprint 2 Plan (Preview)
List of two planned user stories per individual for Sprint 2

Include story IDs/titles and owner assignments

Example format:

Story ID / Name	Owner
US-05 – Profile Edit	Alice
US-06 – Password Reset	Alice
US-07 – Notifications	Bob
US-08 – Settings Page	Bob
 

Sprint 1 Deliverables – Instructor Quick-Check Summary
Item	Description	Points	Criteria / What We Check
Story Board	URL + end-of-sprint screenshot	10	Board shows To Do / In Progress / Review / Done columns; each story linked to branch or PR; reflects actual progress.
Pull Requests (PRs)	One PR per story + links + screenshots	15	Each PR has clear description, at least one teammate approval, and passing CI checks.
Story Implementation Table	Story–Owner–File–Test–Status	20	Table complete and accurate; each story has owner and test case; statuses match board and merged PRs.
CI/CD Evidence	Pipeline setup + badge or screenshot	10	CI/CD runs on PRs (build/lint/test) and shows successful status.
Team Reflection	What went well / not well / next changes + member contributions	15	Reflection shows specific lessons and each member’s input.
Sprint 2 Plan	Two planned stories per individual listed	10	Stories realistic, distinct from Sprint 1, clearly assigned.
In-Class Demo	5–7 minute team presentation of working increment	20	Each member presents their story; features function as intended.
Total		100 pts
💡 Grading Reminder (Read Carefully)
Although Sprint 1 is a team project, your grade is awarded individually based on your contributions and participation.

What this means:

🚫 No contribution = 0 grade.

If you have no commits, no PRs, and do not participate in the demo or report, you will receive 0 points, even if your name appears on the team submission.

💪 Strong individual contribution = solid grade.

Completing your assigned user story with working code, test case(s), and an approved PR will secure a strong individual score, regardless of team variations.

🤝 Helping each other = stronger overall results.

Agile is about collaboration — teams that review each other’s code, fix integration issues, and maintain communication will perform better collectively.

Remember: your team is in one boat — success depends on how well you work together.