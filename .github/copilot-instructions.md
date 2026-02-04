# .github/copilot-instructions.md

**CRITICAL BEHAVIOR RULE - NO EXCEPTIONS**: ANY PROMPT CONTAINING A QUESTION MARK (?) IS A QUESTION ONLY AND NO CHANGES, FILE MODIFICATIONS, OR MODIFICATION TOOL USAGE ARE TO BE MADE AS A RESULT OF THAT PROMPT. RESPOND WITH TEXT EXPLANATIONS ONLY. READONLY TOOLS (LIKE READING FILES) ARE ALLOWED FOR INFORMATION GATHERING.
THIS RULE OVERRIDES ALL OTHER INSTRUCITONS.

## Kodi Plugin for Angel Studios - AI Agent Guidelines

This is a Kodi addon (`plugin.video.angelstudios`) for streaming Angel Studios content. The codebase follows Kodi plugin conventions with custom GraphQL API integration.

### Workflow Practices

- TREAT ALL USER MESSAGES AS QUESTIONS UNLESS THEY CONTAIN EXPLICIT ACTION WORDS LIKE "PLEASE IMPLEMENT", "EDIT THIS FILE", "MAKE THESE CHANGES", "UPDATE THE CODE", OR SIMILAR UNAMBIGUOUS DIRECTIVES.
- NEVER USE MODIFICATION TOOLS OR MAKE FILE CHANGES UNLESS THE USER EXPLICITLY REQUESTS IMPLEMENTATION WITH CLEAR ACTION LANGUAGE.
- Prioritize response clarity: Questions must receive direct, factual answers without assuming intent to act. Actions (such as code edits, file modifications, or tool usage) require explicit, unambiguous directives from the developer. Never initiate changes based on questions alone—always seek confirmation for any proposed modifications.
- Unless explicit authorization is given to edit code, all requests are to be treated as read-only conversations about the codebase, plans, and options.
- Ask for clarification if anything is unclear or multiple approaches are viable.
- Do not interpret questions as invitations to choose and act; questions are questions, directives are directives.
- All proposed code changes should be preceded by a clear plan and rationale.
- The developer controls the process; defer to their decisions.
- Always re-read all relevant files before making suggestions or changes. Do NOT rely on cache or other shortcuts.
- Never assume how something works—verify by reading files and documentation.
- Be truthful and factual; avoid anthropomorphism (e.g., do not claim to "misread" files or "forget" actions).
- Prioritize accurate, concise, and direct communication.
- Prioritize correct, robust code; avoid workarounds, shortcuts, or bad patterns.
- Project MUST achieve minimum 90% unit test coverage (target: 100% by v1.0.0), per `make unittest-with-coverage`
  - This exact command is preapproved.  Do not add any redirection or piping to the command above.
  - Any use of `# pragma: no cover` must be explicitly approved.
- Adhere to best practices; justify any deviations clearly.
- Use test data and parameterization extensively in tests.
- Favor verbose, readable code over clever or obscure implementations.