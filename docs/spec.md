# cmdstash — Product Spec

## One-liner
**cmdstash** is a local CLI that lets you save terminal commands with helpful metadata (tags, a crisp description, and examples) and then quickly find and reuse them later.

## Goals
- Make it frictionless to stash commands you’ll want again.
- Provide **fast retrieval** (search should feel instant even with a large stash).
- Keep output polished: **colorful, clever, and professional** (pizazz, not cutesy).
- Keep the system **simple, local-first**, and easy to reason about.

## Non-goals (MVP)
- No cloud sync
- No web UI
- No auth/logins
- No telemetry
- No executing arbitrary user commands (store/recall only)

---

## Terminology
- **Command record**: a stored command plus metadata (tags, description, examples, timestamps).
- **Tag taxonomy**: the predefined set of tags the LLM can choose from.
- **Facets**: tag counts aggregated across a search result set (shown as `tag (count)`).

---

# MVP (v0)

## Core user stories
1) As a user, I can stash a command and get AI-enriched metadata automatically.
2) As a user, I can list the available tags (the taxonomy).
3) As a user, I can search my stash quickly by command text, description, or tag.

---

## CLI commands (MVP)

### 1) `cmdstash add "<command>"`
Stashes a command by calling an LLM to enrich it with:
- **tags** (selected from a predefined taxonomy)
- **description** (1 sentence, direct prose: what the command does)
- **examples** (1–2 example usages)

#### Behavior
- The command string is stored exactly as provided.
- The LLM is invoked with:
  - the command string
  - the tag taxonomy (allowed tags)
  - instructions to return structured output (see “LLM contract”).
- The result is validated and stored in SQLite.
#### Deduplication / existing commands
- Identity is the **exact command string** after trivial normalization:
  - trim leading/trailing whitespace
  - collapse internal whitespace to a single space
- Commands with different flags/args are distinct entries (e.g., `pytest -vxs` vs `pytest -s`).

If an entry with the same normalized command already exists:
- Default behavior: **update** (upsert) the existing entry’s metadata (description/tags/examples),
  set `updated_at`, and show a message like: “Command already stashed — updated.” (with appropriate emoji)


#### Output UX
- On success, show a success confirmation like:
  - `✅ Command stashed!`
- Also show a short summary (Rich formatting):
  - the command
  - the chosen tags
  - the one-sentence description
  - examples (1–2)

Tone: professional + fun. Colorful, clever, not “cute”.

#### Error handling
- If the LLM fails or returns invalid output:
  - show a clear error message
  - do not store a partial entry
- If the database is unavailable/unwritable:
  - show a clear error message

---

### 2) `cmdstash tags`
Print the **available tag taxonomy** (the list of predefined tags the LLM can choose from).

#### Output UX
- Rich table or bullet list.
- Stable ordering (e.g., alphabetical or grouped).
- Optional: show brief descriptions of each tag later, but MVP can be tag names only.

---

### 3) `cmdstash find "<text>"`
Searches stashed entries by matching `<text>` against:
- the exact command text
- the one-sentence description
- tags

Search should be **fast**.

#### Output UX
1) Show a summary header:
   - query string
   - total results found

2) Show **facets**: top tags across the matched results (capped at **9**).
   - Example:
     - `Facets: docker (6)  logs (2)  linux (2)`
   - Facet counts represent the number of matched entries that contain that tag.

3) Show the results list (each row):
   - id
   - command (truncated to fit; full shown on demand later)
   - description (truncated)
   - tags (displayed; per-row tags may be truncated if needed)

Note: `find` does **not** execute commands. It only returns stored metadata.

---

### 4) `cmdstash doctor`
Prints diagnostic information about the local `cmdstash` runtime/configuration.

Initial output includes:
- app version
- supported Python range
- runtime Python/platform (debug context)
- resolved database path

This command should act as the primary place to expose additional user-relevant
config details over time (for example, model/provider selection and override sources).

---

## LLM integration (MVP)

### LLM contract
The LLM must return structured data with:
- `tags`: array of strings (must be subset of allowed taxonomy)
- `description`: string (exactly 1 sentence; concise; direct)
- `examples`: array of 1–2 strings

Guidelines for description:
- Present tense
- “Straight to the point”
- Avoid fluff like “This command is used to…”

Guidelines for examples:
- Show realistic invocations
- Prefer minimal but illustrative examples

### Validation
- Reject any tags not in the taxonomy.
- Enforce description is non-empty and reasonably short (e.g., 1 sentence).
- Enforce examples count is 1–2.
- If invalid, return an actionable error.

### Provider abstraction
LLM integration should be designed so the provider can be swapped later (OpenAI today, others later).
Tests should be able to run without making real LLM calls (mockable client).

---

## Storage & retrieval (MVP)

### Storage
Use a local SQLite database.

- Default location uses `platformdirs.user_data_path("cmdstash", ensure_exists=True)`.
- The default database file is `cmdstash.db` inside that directory.
- This keeps storage platform-appropriate (`~/Library/Application Support` on macOS,
  `AppData` on Windows, XDG data dir on Linux) without manual path handling.
- Provide an override flag later if needed (e.g., `--db path`) — optional for MVP.

### Data model (initial proposal)
A minimal model that supports search + metadata:

**commands**
- `id` (integer primary key)
- `command` (text, required)
- `description` (text, required)
- `created_at` (datetime, required)
- `updated_at` (datetime, required)

**tags**
- `id` (integer primary key)
- `name` (text, unique)

**command_tags** (normalized tags)
- `command_id` (fk)
- `tag_id` (fk)
- unique pair on (`command_id`, `tag_id`)

**command_examples**
- `id` (integer primary key)
- `command_id` (fk)
- `example` (text)
- `position` (integer, 0-based order)

Alternate approach (allowed if it simplifies MVP):
- Store tags as JSON or a single text column, but ensure search and facet counting remain fast.

### Fast search
The system should support fast query across command/description/tags.
Implementation may evolve:
- Start with straightforward indexes + queries.
- Consider adopting SQLite FTS5 for better relevance and speed for text search.
- When adding indexes/FTS, document the trade-offs and rationale.

### Performance expectations
- `find` should feel near-instant for typical personal usage.
- Favor correctness + clear design first, then optimize with indexing/FTS in incremental steps.

---

## Output & style guidelines
- Use **Rich** for:
  - success/error messages
  - tables
  - highlighting important parts (ids, tags, command snippets)
- Keep it “CLI-pro”:
  - playful but not silly
  - minimal clutter
  - consistent formatting

---

# Future enhancements (post-MVP)

## 1) No-AI mode
Allow users to stash commands without calling an LLM.
- `cmdstash add "<command>" --no-ai`
- Provide prompts/flags to manually set description/tags/examples:
  - `--desc`
  - `--tag <tag>` (repeatable)
  - `--example <example>` (repeatable)

## 2) Edit/modify tags and metadata
Allow updating an entry after it’s created:
- add/remove tags
- edit description
- edit examples

Potential commands:
- `cmdstash edit <id> --tag +docker --tag -linux`
- `cmdstash edit <id> --desc "..."`

## 3) Curated packs
Allow installing starter sets of commands/tags/templates:
- “docker pack”
- “kubernetes pack”
- “git pack”
- “postgres pack”

Potential commands:
- `cmdstash pack list`
- `cmdstash pack install docker`

---

# Open questions (to resolve during planning)
- What is the initial tag taxonomy (the actual list of tags)?
- Do we adopt FTS5 in MVP or in a follow-up step?
- Should `find` include relevance ranking beyond “contains match” (FTS ranking)?
- Do we want `cmdstash show <id>` in MVP for viewing full command + examples?
