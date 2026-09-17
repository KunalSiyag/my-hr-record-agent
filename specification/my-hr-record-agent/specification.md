# My HR Record Agent — Asset Specification

> **Guidelines**: Read [../guidelines.md](../guidelines.md) and [../guidelines-agent.md](../guidelines-agent.md) before executing ANY tasks below.
> **Python details**: [../guidelines-agent-python.md](../guidelines-agent-python.md)
> **MCP integration**: [../guidelines-agent-mcp.md](../guidelines-agent-mcp.md)
> **Runtime skills**: [../guidelines-agent-skills.md](../guidelines-agent-skills.md)

Asset name: `my-hr-record-agent`
Asset type: AI Agent (Python, A2A protocol)

## API Specs Available

The following OData EDMX specs are in `specification/my-hr-record-agent/api-specs/`:

| File | API Name | ORD ID |
|------|----------|--------|
| `personal-information.edmx` | EC Personal Information | `sap.sf:apiResource:ECPersonalInformation:v1` |
| `employment-information.edmx` | EC Employment Information | `sap.sf:apiResource:ECEmploymentInformation:v1` |
| `skills-management.edmx` | EC Skills Management | `sap.sf:apiResource:ECSkillsManagement:v1` |
| `employee-profile.edmx` | EC Employee Profile | `sap.sf:apiResource:ECEmployeeProfile:v1` |
| `global-assignment.edmx` | EC Global Assignment | `sap.sf:apiResource:ECGlobalAssignment:v1` |
| `employee-global-information.edmx` | Employee Global Information | `sap.sf:apiResource:EmployeeCentralEC:v1` |

---

## Phase 1 — Solution Setup

- [ ] Invoke `setup-solution` skill to create `solution.yaml` and `assets/my-hr-record-agent/asset.yaml`
- [ ] Confirm `solution.yaml` exists at project root and is well-formed
- [ ] Confirm `assets/my-hr-record-agent/asset.yaml` exists and uses `buildPath: .`

---

## Phase 2 — MCP Translation Files

For each API spec below, invoke the `mcp-translation-file` skill to generate an MCP translation file. Do NOT manually create translation files.

- [ ] Generate MCP translation file for `personal-information.edmx`
  - API ORD ID: `sap.sf:apiResource:ECPersonalInformation:v1`
  - Spec path: `specification/my-hr-record-agent/api-specs/personal-information.edmx`
  - Output directory: `specification/my-hr-record-agent/mcps/personal-information/`

- [ ] Generate MCP translation file for `employment-information.edmx`
  - API ORD ID: `sap.sf:apiResource:ECEmploymentInformation:v1`
  - Spec path: `specification/my-hr-record-agent/api-specs/employment-information.edmx`
  - Output directory: `specification/my-hr-record-agent/mcps/employment-information/`

- [ ] Generate MCP translation file for `skills-management.edmx`
  - API ORD ID: `sap.sf:apiResource:ECSkillsManagement:v1`
  - Spec path: `specification/my-hr-record-agent/api-specs/skills-management.edmx`
  - Output directory: `specification/my-hr-record-agent/mcps/skills-management/`

- [ ] Generate MCP translation file for `employee-profile.edmx`
  - API ORD ID: `sap.sf:apiResource:ECEmployeeProfile:v1`
  - Spec path: `specification/my-hr-record-agent/api-specs/employee-profile.edmx`
  - Output directory: `specification/my-hr-record-agent/mcps/employee-profile/`

- [ ] Generate MCP translation file for `global-assignment.edmx`
  - API ORD ID: `sap.sf:apiResource:ECGlobalAssignment:v1`
  - Spec path: `specification/my-hr-record-agent/api-specs/global-assignment.edmx`
  - Output directory: `specification/my-hr-record-agent/mcps/global-assignment/`

- [ ] Generate MCP translation file for `employee-global-information.edmx`
  - API ORD ID: `sap.sf:apiResource:EmployeeCentralEC:v1`
  - Spec path: `specification/my-hr-record-agent/api-specs/employee-global-information.edmx`
  - Output directory: `specification/my-hr-record-agent/mcps/employee-global-information/`

- [ ] Verify translation files exist:
  ```bash
  ls specification/my-hr-record-agent/mcps/*/translation.json
  ls specification/my-hr-record-agent/mcps/*/.tool-list.json
  ```

---

## Phase 3 — MCP Server Assets

For each generated MCP translation file, invoke the `setup-solution` skill to create a corresponding MCP server asset.

- [ ] Create MCP server asset for Personal Information MCP
- [ ] Create MCP server asset for Employment Information MCP
- [ ] Create MCP server asset for Skills Management MCP
- [ ] Create MCP server asset for Employee Profile MCP
- [ ] Create MCP server asset for Global Assignment MCP
- [ ] Create MCP server asset for Employee Global Information MCP

After each MCP server asset is created, read its `asset.yaml` and copy the exact `ordId` value for use in the agent's `asset.yaml`.

```bash
grep '^ordId:' assets/<mcp-server-asset-name>/asset.yaml
```

---

## Phase 4 — Agent Bootstrap

- [ ] Navigate to `assets/my-hr-record-agent/` and invoke the `sap-agent-bootstrap` skill to scaffold the agent project
- [ ] Confirm the following files exist after bootstrap:
  - `assets/my-hr-record-agent/asset.yaml`
  - `assets/my-hr-record-agent/app/agent.py`
  - `assets/my-hr-record-agent/app/main.py`
  - `assets/my-hr-record-agent/app/mcp_tools.py`
  - `assets/my-hr-record-agent/requirements.txt`
  - `assets/my-hr-record-agent/requirements-test.txt`
  - `assets/my-hr-record-agent/prebuilt_tests/`

---

## Phase 5 — MCP Server Dependencies in asset.yaml

- [ ] Add a `requires` entry in `assets/my-hr-record-agent/asset.yaml` for each MCP server asset created in Phase 3.
  - Use the exact `ordId` value from each MCP server's `asset.yaml` — never invent or guess.
  - All entries must use `kind: mcp-server`.

Example structure (use actual ORD IDs from Phase 3):
```yaml
requires:
  - name: personal-information-mcp-server
    kind: mcp-server
    ordId: <exact-ord-id-from-phase-3>
  - name: employment-information-mcp-server
    kind: mcp-server
    ordId: <exact-ord-id-from-phase-3>
  - name: skills-management-mcp-server
    kind: mcp-server
    ordId: <exact-ord-id-from-phase-3>
  - name: employee-profile-mcp-server
    kind: mcp-server
    ordId: <exact-ord-id-from-phase-3>
  - name: global-assignment-mcp-server
    kind: mcp-server
    ordId: <exact-ord-id-from-phase-3>
  - name: employee-global-information-mcp-server
    kind: mcp-server
    ordId: <exact-ord-id-from-phase-3>
```

---

## Phase 6 — Mock MCP Config

- [ ] Invoke the `mcp-mock-config` skill to generate `assets/my-hr-record-agent/mcp-mock.json` for testing
- [ ] Verify `assets/my-hr-record-agent/mcp-mock.json` exists and contains mock data for all 6 MCP servers

---

## Phase 7 — Agent Implementation

### 7.1 — System Prompt

- [ ] Write the agent system prompt in `app/agent.py` using the `@prompt_section` decorator.
  The system prompt MUST include the following instructions:
  - You are a read-only HR self-service agent. You help employees view and export their own HR record from SAP SuccessFactors Employee Central.
  - You MUST only access HR data for the authenticated employee (identified by their session-derived `personIdExternal` / `userId`). Never access data for any other employee.
  - You MUST use tools to retrieve all HR data. Never fabricate, guess, or invent data values.
  - All API interactions are read-only. Never attempt to create, update, or delete any data.
  - When calling tools that support pagination, always set the page size parameter to a maximum of 100 to prevent context overflow.
  - If a tool returns an error, report the error message exactly as received.

### 7.2 — Agent Decorators

- [ ] Add `@agent_model` for primary model (e.g. `gpt-4o`)
- [ ] Add `@agent_model` for fallback model (e.g. `gpt-4o-mini`)
- [ ] Add `@agent_config` for temperature (e.g. `0.0` for deterministic HR data retrieval)
- [ ] Add `@agent_config` for agent memory TTL
- [ ] Confirm exactly 5 decorators are present (2× `@agent_model`, 2× `@agent_config`, 1× `@prompt_section`)
- [ ] Verify `sap_cloud_sdk.agent_decorators` import is present

### 7.3 — HR Data Retrieval Tools (via MCP)

All HR data must be retrieved through MCP tools. The agent must load tools lazily using the canonical pattern from `guidelines-agent-python.md`.

The agent should be able to handle requests such as:
- "Show me my HR record"
- "What personal information does HR have about me?"
- "Show my employment details"
- "What skills and profile data is recorded for me?"
- "Who are my emergency contacts?"
- "What addresses does HR have on file for me?"
- "Do I have any global assignments?"
- "Download my HR record as PDF"
- "Download my HR record as JSON"

### 7.4 — HR Record Completeness Checker

- [ ] Implement a `check_completeness(hr_data: dict) -> dict` function in `app/hr_completeness.py`
  - Input: a dict with keys for each HR section (personal_info, employment, skills_profile, emergency_contacts, addresses, global_assignments)
  - For each section, evaluate whether the data is: "complete" (all expected fields populated), "partial" (some fields populated), or "missing" (no data returned)
  - Expected field sets per section:
    - **personal_info**: firstName, lastName, dateOfBirth, countryOfBirth, gender, nationality
    - **employment**: startDate, jobTitle, department, company, employmentType, emplStatus
    - **skills_profile**: at least one skill or competency returned
    - **emergency_contacts**: at least one contact with name and phone
    - **addresses**: at least one address with address1 and city
    - **global_assignments**: presence checked — "not applicable" if empty (not flagged as missing)
  - Return a structured completeness report dict

### 7.5 — PDF Export

- [ ] Implement `generate_pdf(hr_data: dict, completeness: dict) -> bytes` in `app/hr_export.py`
  - Use `reportlab` or `fpdf2` library (add to `requirements.txt`)
  - Render a clean, readable PDF with:
    - Header: "My HR Record — [Employee Name]" and generation date
    - One section per HR data domain
    - Completeness status badge per section (✓ Complete / ⚠ Partial / ✗ Missing)
    - All fields displayed as label: value
  - Return PDF bytes

### 7.6 — JSON Export

- [ ] Implement `generate_json(hr_data: dict, completeness: dict) -> str` in `app/hr_export.py`
  - Serialise the consolidated HR record and completeness report to a formatted JSON string
  - Include metadata: `generated_at`, `employee_id`, `completeness_summary`
  - Return JSON string

### 7.7 — Consolidated HR View in Agent Response

- [ ] When the employee asks to see their record, the agent should:
  1. Resolve the employee's `personIdExternal` from the session context (use a constant `EMPLOYEE_SCOPE_KEY = "person_id_external"` in `app/agent.py`)
  2. Fetch all 6 HR data sections in parallel where possible
  3. Run the completeness check
  4. Present the consolidated view in a readable, plain-language format
  5. Offer to export as PDF and/or JSON
  6. If the employee requests an export, generate the file and return it as a downloadable artifact

### 7.8 — Runtime Skill: HR Record Retrieval

- [ ] Create `app/skills/hr-record-retrieval/SKILL.md` with instructions for:
  - How to identify the requesting employee's `personIdExternal` from session context
  - How to handle each API section (which MCP tool names to look for, what to do with empty responses)
  - How to present the completeness summary in a clear, plain-language format
  - Export workflow: offer PDF and JSON, generate on request

---

## Phase 8 — OpenTelemetry Instrumentation (Milestones)

- [ ] Ensure `auto_instrument()` is called at the top of `app/main.py` before any AI framework imports
- [ ] Import `tracer` from the bootstrap-provided telemetry module

Implement the following milestone log statements in the agent's main processing flow:

- [ ] **M1 — Employee Identity Confirmed**
  - `logger.info("[M1.achieved]: employee identity confirmed, employee_id resolved from session")`
  - `logger.warning("[M1.missed]: employee identity could not be resolved — session context did not yield a valid employee_id")`
  - Emit an OpenTelemetry span: `"m1-employee-identity-confirmed"`

- [ ] **M2 — All Data Sections Fetched**
  - `logger.info("[M2.achieved]: all HR data sections fetched — personal_info, employment, skills_profile, emergency_contacts, addresses, global_assignments")`
  - `logger.warning("[M2.missed]: one or more HR data section retrievals did not complete — sections_attempted=[list], sections_failed=[list]")`
  - Emit an OpenTelemetry span: `"m2-all-data-sections-fetched"`

- [ ] **M3 — Completeness Check Done**
  - `logger.info("[M3.achieved]: completeness check completed — complete=[list], partial=[list], missing=[list]")`
  - `logger.warning("[M3.missed]: completeness check did not complete — reason=[description]")`
  - Emit an OpenTelemetry span: `"m3-completeness-check-done"`

- [ ] **M4 — Consolidated View Presented**
  - `logger.info("[M4.achieved]: consolidated HR record view presented to employee")`
  - `logger.warning("[M4.missed]: consolidated view was not presented — reason=[description]")`
  - Emit an OpenTelemetry span: `"m4-consolidated-view-presented"`

- [ ] **M5 — Export Delivered**
  - `logger.info(f"[M5.achieved]: export delivered — formats=[format_list]")`
  - `logger.warning("[M5.missed]: export was not generated or delivered — formats_requested=[list], reason=[description]")`
  - Emit an OpenTelemetry span: `"m5-export-delivered"`

- [ ] Verify instrumentation:
  ```bash
  grep -r "M[0-9]\.achieved" assets/my-hr-record-agent/app/
  ```

---

## Phase 9 — Tests

Working directory for all test operations: `assets/my-hr-record-agent/`

### 9.1 — Install test dependencies
- [ ] `pip install -r requirements-test.txt`

### 9.2 — Unit Tests (one per tool/module)

- [ ] Write `tests/test_completeness.py` — unit tests for `hr_completeness.check_completeness()`
  - Test: all sections complete → all "complete"
  - Test: empty emergency contacts → "missing"
  - Test: empty global assignments → "not applicable" (not "missing")
  - Test: partial employment data (some fields missing) → "partial"

- [ ] Write `tests/test_export_json.py` — unit test for `hr_export.generate_json()`
  - Test: valid hr_data produces valid JSON string with expected top-level keys

- [ ] Write `tests/test_export_pdf.py` — unit test for `hr_export.generate_pdf()`
  - Test: valid hr_data produces non-empty bytes output

- [ ] Write `tests/test_agent.py` — integration test for end-to-end agent flow
  - Mock all MCP tools using the `mcp-mock.json` fixture via `conftest.py`
  - Mock the LLM (ChatLiteLLM) to return a canned response
  - Test: agent receives "show my HR record" → retrieves data → performs completeness check → returns a response containing completeness status
  - Test: agent receives "download my HR record as JSON" → calls export → returns JSON artifact
  - All external calls (MCP servers, AI Core) MUST be mocked — tests must run offline

### 9.3 — Run Tests
- [ ] Run `pytest` from `assets/my-hr-record-agent/` (no extra flags)
- [ ] Verify coverage ≥ 70%; if below, add targeted tests until threshold met
- [ ] Confirm `test_report.json` is generated after the full run

---

## Phase 10 — Validation Checklist

Run all checks before marking implementation complete:

```bash
# Instrumentation
grep -r "M[0-9]\.achieved" assets/my-hr-record-agent/app/     # must return results

# Decorators
grep -r "sap_cloud_sdk.agent_decorators" assets/my-hr-record-agent/app/  # must return results
grep -c "^@agent_model\|^@agent_config\|^@prompt_section" assets/my-hr-record-agent/app/agent.py  # must return 5

# Test report
ls assets/my-hr-record-agent/test_report.json   # must exist

# MCP server dependencies
grep "kind: mcp-server" assets/my-hr-record-agent/asset.yaml  # must return 6 entries
```
