# My AI Coding Playbook

## 1. When I reach for AI first

- When I need help understanding code or a technical problem. I use AI to explain what is happening and suggest where I should investigate.
- When I need to find bugs or edge cases. I use AI to suggest possible problems and tests, then I verify them myself.
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

- I check AI claims against the real source. I compare AI's answer with the actual files, code, documentation, or git commits instead of accepting its summary as proof.
- I question what AI does not mention. If something important is missing, I investigate it myself. This helped me catch the CLAUDE.md context leaks instead of assuming the AI's summary was complete.
- I make sure I understand the code before accepting it. I trace important changes line-by-line and make sure I can explain what the code does. If I cannot explain it, I do not consider the work fully verified.

## 5. What I am still figuring out

- How much I should trust AI-generated summaries and structured context. The CLAUDE.md incidents showed me that AI can give a useful summary while still missing or leaking important context, so I am still figuring out how much I should rely on these summaries.
- How to record AI contributions consistently. I know I should document what AI contributed and what I verified myself, but I am still developing a simple habit that I can use consistently without creating too much extra work.
- How to use AI effectively without becoming dependent on it. I am still learning when AI genuinely saves time and when doing the thinking myself first produces a better result.

## Decision Card

- For a new feature I reach for: AI to help me understand requirements, brainstorm an approach, and identify edge cases — it gives me a starting point without handing over the decision.
- For a code review I reach for: AI as a second reviewer, then I compare its findings with the actual code and decide validity myself.
- For debugging I reach for: AI to identify possible causes and suggest tests, but I reproduce the problem and verify the fix myself.
- For infrastructure I reach for: documentation and my own inspection first, then AI to explain configuration or troubleshoot specific problems — infrastructure changes have wider consequences, so I don't want AI making changes blindly.
- I will never paste company passwords, API keys, customer personal information, or confidential company data into an AI tool.
- My one rule is: use AI to help me think and work faster, but never let it replace my judgment or verification.