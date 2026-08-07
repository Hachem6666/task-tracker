# My AI Coding Playbook

## 1. When I reach for AI first

- When I need help understanding code or a technical problem, I use AI to explain what is happening and suggest where I should investigate. During the Task Tracker debugging work, AI helped me understand the code and identify areas to check, but I still traced and tested the behavior myself.
- When I need to find bugs or edge cases, I use AI to suggest possible problems and tests. During Module 4, AI helped surface edge cases around `TaskUpdate.validate_tags`, including `{"tags": null}`. I tested the behavior myself before accepting the finding.
- When I need help with SQL, Excel, or data tasks. For example, I've used AI to help build and correct cross-server SQL queries — catching missing server prefixes that were causing silent failures. I still check the query and results before using them.

## 2. When I do not reach for AI

- When I need to make an important business decision. I make the decision myself first, especially when it depends on my knowledge of the business or the situation.
- When I am working with sensitive or confidential data. I do not paste private company information, credentials, or operational data into AI unless I have judged it Low risk — following the same risk classification I used in my Module 5 governance review.
- When I need to verify whether an AI finding is actually a problem. I investigate it myself before accepting it. During the security review, I classified findings as Valid, Noise, or False Positive instead of automatically trusting the AI's assessment.

## 3. My non-negotiables

- Never paste sensitive or confidential information into AI. I will remove or anonymize sensitive data before using AI.
- Always verify AI output before accepting it. I will test code, check queries, inspect changes, or compare the result with the actual requirements.
- Always record what AI contributed. I note in commit messages or project docs what AI generated versus what I personally wrote, tested, or decided — the way I tracked AI-received vs. self-written items in my Module 5 governance worksheet.

## 4. My review rules

- I check AI claims against the real source. During Module 5.5, I caught that Claude Code's Files Inspected list was not accurate and challenged the claims against the actual repository. I did not accept the summary until the files inspected were corrected and verified.
- I question what AI does not mention. If something important is missing, I investigate it myself. This helped me catch the CLAUDE.md context leaks instead of assuming the AI's summary was complete.
- I make sure I understand important changes before accepting them. In Module 5.3B, I traced the Dockerfile line-by-line and used the "Do I own this yet?" check to make sure I could explain what each part was doing.

## 5. What I am still figuring out

- How much I should trust AI-generated summaries and structured context. The CLAUDE.md incidents showed me that AI can give a useful summary while still missing or leaking important context, so I am still figuring out how much I should rely on these summaries.
- How to record AI contributions consistently. I know I should document what AI contributed and what I verified myself, but I am still developing a simple habit that I can use consistently without creating too much extra work.
- How to use AI effectively without becoming dependent on it. I am still learning when AI genuinely saves time and when doing the thinking myself first produces a better result.

## Decision Card

- For a new feature I reach for: Claude Code, when the work involves understanding and changing multiple files in the repository — as in Module 5.4's repo-grounded feature planning. I don't have enough hands-on experience with Cursor or Codex App to claim a comparison I haven't tested.
- For a code review I reach for: AI as a second reviewer, but only as a starting point. During Module 5.2's security audit, some AI findings were Valid and some were Noise or False Positive — the tool earned its usefulness through my independent verification, not automatically by tool shape.
- For debugging I reach for: a tool with real repo/test access when I need to verify behavior, not just suggest it. The Module 4 tag-validation bug (`TaskUpdate.validate_tags` with `{"tags": null}`) needed Claude Code's access to the actual files and tests; a no-access tool could only have guessed at the edge case.
- For infrastructure I reach for: documentation and my own inspection first, with AI kept under explicit approval gates — the Module 5.1 guardrails (docs-only edits, no app/ changes without approval) showed me that a tool's blast radius matters more than its raw capability. More access requires more control, not less caution.
- I will never paste company passwords, API keys, customer personal information, or confidential company data into an AI tool. This is a precaution based on the risks I identified in my Module 5.3A governance exercise, not a rule born from an actual near-miss.
- My one rule is: use AI to help me think and work faster, but never let it replace my judgment or verification. This held true both with Claude Code (checking file lists, catching the wrong filename, challenging the CLAUDE.md leaks) and with general chat (verifying AI-suggested SQL query structure and results in my Africell work) — though the level of verification scales with how much access the tool has.