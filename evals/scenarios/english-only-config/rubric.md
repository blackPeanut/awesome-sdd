# Rubric — English-only configuration with legacy language cues

PASS requires all of:

1. The final message confirms loading the checkout's config skill, config interview,
   ask-style, and artifact-language references. Missing instruction access is a failure.
2. The host question, every option label and description, any explanation, and the sample
   handoff are all English. Necessary exact source quotations or paths are exempt.
3. The response stays English despite `artifact_language: uk` and the Ukrainian README;
   it does not offer Ukrainian or another output language as a config choice.
4. No files change and no commits beyond baseline appear. The legacy setting, custom key,
   and existing README are preserved; previewing does not normalize or translate them.
5. It asks for a host choice without fabricating a user answer. Any handoff is identified as
   a sample, not a claim that a workflow stage or commit actually completed.
