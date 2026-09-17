# Product Requirements Document (PRD)

**Title:** My HR Record Agent  
**Date:** 2026-09-11  
**Owner:** HR Product Owner  
**Solution Category:** AI Agent

---

## Product Purpose & Value Proposition

**Elevator Pitch:**  
Employees have no single place to see all the HR data that SuccessFactors holds about them. This agent solves that — on request, it gathers every piece of an employee's own record, clearly shows what is present and what is missing, and hands back a downloadable PDF and JSON export, all without involving the HR team.

**Business Need:**  
Retrieving a complete personal HR record today requires navigating multiple screens in SuccessFactors or submitting a manual request to HR. There is no self-service capability that consolidates personal information, employment details, skills, emergency contacts, addresses, and global assignments into one view. Employees lack visibility into their own data, and HR teams spend time fielding requests that could be fully automated.

**Expected Value:**  
- Employees get a complete, accurate view of their HR record on demand, with zero HR team involvement.
- Data quality issues (missing or inconsistent fields) are surfaced immediately to the employee.
- HR teams are freed from manual record-retrieval requests.

**Product Objectives (Prioritized):**
1. Deliver 100% field coverage — every expected HR data section is retrieved and presented, with explicit status for any missing section.
2. Eliminate manual HR involvement — zero HR interventions required per employee self-service request.
3. Ensure data consistency — no discrepancies between sections surfaced in the same response.
4. Provide dual-format export — employee can download their record as both PDF and JSON.

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| HR data fields coverage | — | 100% of fields returned with no gaps | — | Employee self-service HR record retrieval | user |
| Manual HR team involvement for data requests | — | 0 interventions per request | — | Employee Administration (SuccessFactors) | user |
| Data consistency across sections | — | Zero discrepancies between sections | — | Employee information & reporting | user |

---

## User Profiles & Personas

### Primary Persona: Alex — Employee

Alex is a 34-year-old mid-level professional working in a multinational company that uses SAP SuccessFactors for HR management. Alex works partly remotely and partly on-site, using a laptop daily. Alex is comfortable with standard business software but is not technically minded. Alex occasionally needs to verify their own HR record — for visa applications, internal transfers, banking proof-of-employment requests, or compliance checks. Currently, getting a complete record means either navigating several different SuccessFactors screens or emailing the HR helpdesk and waiting. Alex wants a simple, trustworthy, and immediate way to see and download all the data held about them — without needing HR to get involved.

**Goals:**
- See a complete, accurate view of all HR data held about them in one place.
- Download their HR record in a format accepted by external authorities (PDF) and for personal archiving (JSON).
- Know immediately if any section of their record is incomplete or missing.

**Key Tasks:**
- Ask the agent to show their full HR record.
- Review each section (personal info, employment, skills, emergency contacts, address, global assignments).
- Download the record as PDF and/or JSON.
- Identify and act on any flagged missing data.

### Secondary Persona: HR Administrator

An HR administrator who monitors system usage and audits self-service interactions. Does not interact with the agent directly for employee record retrieval, but benefits from having a fully automated channel that reduces their manual workload for record requests.

---

## Product Principles

1. **Employee-only access**: The agent never reads or exposes any record other than that of the authenticated requesting employee.
2. **Read-only, always**: The agent performs no writes, updates, or deletions — it is purely observational.
3. **Completeness before export**: The agent always runs a completeness check and flags missing sections before offering an export.
4. **Transparency over assumption**: If a data section is empty or unavailable, the agent says so explicitly rather than silently omitting it.
5. **Plain language**: Responses are written for a non-technical employee, not for an HR system administrator.

---

## Goals and Non-Goals

### Goals (In Scope)

- Retrieve and consolidate all six HR data domains for the requesting employee: personal information, employment details, skills and profile, emergency contacts, addresses, and global assignments.
- Detect and clearly communicate missing or empty sections.
- Generate a PDF export of the consolidated record.
- Generate a JSON export of the consolidated record.
- Operate strictly on the authenticated employee's own record (no cross-employee access).
- Remain entirely read-only.

### Non-Goals (Out of Scope)

- Updating, correcting, or submitting changes to any HR data.
- Accessing records for any employee other than the one making the request.
- Integration with HR systems other than SAP SuccessFactors Employee Central.
- Providing analytics, trend views, or comparison against other employees.
- Acting as an HR helpdesk or answering policy questions.

---

## Requirements

### Must-Have Requirements

**R-01**: Retrieve Personal Information

- **Problem to Solve**: Employees cannot quickly access their own name, date of birth, nationality, and contact details held in SuccessFactors.
- **User Story**: As an employee, I need the agent to retrieve my personal information from SuccessFactors so that I can verify what HR holds about me without navigating multiple system screens.
- **Acceptance Criteria**:
  - Given I am an authenticated employee, when I ask to see my HR record, then the agent returns my personal information fields from SuccessFactors Employee Central.
  - Given a personal information field is empty or absent, when the agent presents my record, then the missing field is clearly flagged rather than silently omitted.
- **Maps to Objective**: 1, 3
- **Priority Rank**: 1

**R-02**: Retrieve Employment Details

- **Problem to Solve**: Employment-related information (position, department, hire date, employment type) is spread across multiple SuccessFactors screens and not easily retrievable as a single view.
- **User Story**: As an employee, I need the agent to retrieve my employment details so that I have an authoritative record for use in official requests such as proof-of-employment letters.
- **Acceptance Criteria**:
  - Given I am authenticated, when I request my HR record, then employment details including position, department, hire date, and employment type are included.
  - Given any employment field is missing, when the record is presented, then the gap is explicitly stated.
- **Maps to Objective**: 1, 3
- **Priority Rank**: 2

**R-03**: Retrieve Skills and Profile

- **Problem to Solve**: Employees cannot easily see what skills and profile data HR holds about them in SuccessFactors.
- **User Story**: As an employee, I need to see the skills and profile data attributed to me so that I can verify accuracy and completeness.
- **Acceptance Criteria**:
  - Given I am authenticated, when I request my HR record, then my skills list and profile data are included in the response.
  - Given the skills section is empty, when the record is presented, then it is flagged as "not populated" rather than omitted.
- **Maps to Objective**: 1, 3
- **Priority Rank**: 3

**R-04**: Retrieve Emergency Contacts and Addresses

- **Problem to Solve**: Emergency contact and address information held by HR is not visible to the employee without HR access.
- **User Story**: As an employee, I need to see my emergency contacts and address records held in SuccessFactors so that I can confirm they are up to date.
- **Acceptance Criteria**:
  - Given I am authenticated, when I request my HR record, then all emergency contacts and home/work addresses on file are returned.
  - Given no emergency contact is on file, when the record is presented, then this is explicitly flagged.
- **Maps to Objective**: 1, 3
- **Priority Rank**: 4

**R-05**: Retrieve Global Assignments

- **Problem to Solve**: Employees with global assignments have no self-service view of those assignment records.
- **User Story**: As an employee, I need to see any global assignments associated with my record so that I have a complete picture of my employment history.
- **Acceptance Criteria**:
  - Given I am authenticated, when I request my HR record, then any global assignment records are included.
  - Given no global assignments exist, when the record is presented, then the section is shown as "not applicable" rather than hidden.
- **Maps to Objective**: 1, 3
- **Priority Rank**: 5

**R-06**: Completeness Check and Missing-Field Reporting

- **Problem to Solve**: Employees do not know whether their HR record is complete or has gaps unless HR manually reviews it.
- **User Story**: As an employee, I need the agent to tell me which sections of my HR record are fully populated and which are missing or incomplete so that I can take action if needed.
- **Acceptance Criteria**:
  - Given all sections have been retrieved, when the agent presents the consolidated view, then it includes a clear completeness summary showing each section as "complete", "partial", or "missing".
  - Given a section is missing or empty, when the completeness summary is shown, then the specific section name is identified.
- **Maps to Objective**: 1, 3
- **Priority Rank**: 6

**R-07**: Export as PDF

- **Problem to Solve**: Employees need a portable, formatted document of their HR record for official use (e.g., visa applications, loan applications).
- **User Story**: As an employee, I need to download my HR record as a PDF so that I can submit it to external authorities or institutions.
- **Acceptance Criteria**:
  - Given a consolidated HR record has been retrieved, when I request a PDF export, then the agent generates and provides a downloadable PDF containing all sections and the completeness summary.
- **Maps to Objective**: 4
- **Priority Rank**: 7

**R-08**: Export as JSON

- **Problem to Solve**: Employees may need a machine-readable version of their HR record for personal archiving or downstream use.
- **User Story**: As an employee, I need to download my HR record as a JSON file so that I can archive it or use it programmatically.
- **Acceptance Criteria**:
  - Given a consolidated HR record has been retrieved, when I request a JSON export, then the agent generates and provides a downloadable JSON file with all sections structured as key-value data.
- **Maps to Objective**: 4
- **Priority Rank**: 8

**R-09**: Self-Scoping and Read-Only Enforcement

- **Problem to Solve**: An agent with access to SuccessFactors APIs must be strictly prevented from accessing any employee's record other than the person making the request, and must never modify data.
- **User Story**: As an employee, I need to be confident that the agent only accesses my own HR record and cannot read or write any other employee's data.
- **Acceptance Criteria**:
  - Given any request, when the agent makes API calls, then only the authenticated user's employee ID is used as the query scope.
  - Given any request, when the agent interacts with SuccessFactors, then no write, update, or delete operations are performed.
  - Given an attempt to query another employee's record (e.g., by supplying an ID), when the agent processes the request, then it refuses and explains it can only access the requester's own record.
- **Maps to Objective**: 1, 2, 3
- **Priority Rank**: 1 (security constraint — applies across all requirements)

---

## Solution Architecture

**Architecture Overview:**  
A Python AI agent (A2A protocol) deployed on SAP BTP. The agent connects to SAP SuccessFactors Employee Central via its OData APIs, assembles the retrieved data into a consolidated view, performs a completeness check, and generates PDF and JSON export files on request. All API interactions are read-only and scoped to the authenticated employee's own record.

**Key Components:**

- **Agent Runtime**: Python-based A2A agent hosted on SAP BTP, handling conversation, data orchestration, completeness evaluation, and export generation.
- **SuccessFactors OData API Tools**: MCP-wrapped OData API calls covering Personal Information, Employment Information, Skills Management, Employee Profile, Employee Global Information (contacts/addresses), and Global Assignment.
- **Completeness Checker**: Agent logic that evaluates each retrieved section against an expected field set and produces a structured present/missing status.
- **PDF Renderer**: Component that formats the consolidated HR record into a PDF document.
- **JSON Formatter**: Component that serialises the consolidated HR record into a structured JSON file.

**Integration Points:**

- SAP SuccessFactors Employee Central — OData APIs (read-only): Personal Information, Employment Information, Skills Management, Employee Profile, Employee Global Information, Global Assignment.
- Authentication via the employee's SAP BTP session to scope all queries to their own employee ID.

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
- The agent is designed with modular data-retrieval tools — each HR data domain (personal info, employment, skills, emergency contacts, addresses, global assignments) is a discrete, independently callable tool. New data domains can be added by registering additional tools without modifying core agent logic.
- The completeness checker uses a configurable expected-field registry, allowing administrators to add or remove expected fields per section without code changes.
- Export formats (PDF, JSON) are pluggable — additional formats can be registered as new export tools.

**Business Step Instrumentation:**
- All key business steps emit structured log statements following the pattern: `[MILESTONE_ID].[achieved|missed]: [description]`
- Log statements are defined in the Milestones section below and must be implemented exactly as specified to support observability and monitoring in production.

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent (read-only, bounded scope)

**Actions the system performs without human approval:**
- Retrieve all HR data sections from SuccessFactors for the authenticated employee.
- Evaluate completeness of each section.
- Assemble the consolidated view.
- Generate PDF and JSON export files.

**Actions that require human review or approval:**
- None — the agent is entirely read-only and does not trigger any approval workflows.

**Model or engine used:** Large language model via SAP Generative AI Hub for conversation and orchestration; deterministic logic for completeness evaluation and export generation.

**Knowledge & data sources accessed:**
- SAP SuccessFactors Employee Central OData APIs (read-only, scoped to requesting employee).

**Tools or connectors invoked:**
- `get_personal_information` — retrieves personal information fields (read-only)
- `get_employment_information` — retrieves employment details (read-only)
- `get_skills_and_profile` — retrieves skills list and employee profile (read-only)
- `get_emergency_contacts_and_addresses` — retrieves emergency contacts and address records (read-only)
- `get_global_assignments` — retrieves global assignment records (read-only)
- `check_completeness` — evaluates retrieved data against expected field set (local, no API call)
- `export_pdf` — generates a PDF export of the consolidated record (local, no API call)
- `export_json` — generates a JSON export of the consolidated record (local, no API call)

**Guardrails & fail-safes:**
- The agent never uses any employee ID other than the one derived from the authenticated session — hard-coded enforcement, not prompt-level.
- All SuccessFactors API calls are GET-only; any non-GET HTTP method is prohibited.
- If any single data section fails to retrieve, the agent continues with the remaining sections, marks the failed section as "unavailable", and informs the employee of the partial result rather than aborting.
- If authentication cannot be resolved to a valid employee ID, the agent refuses to proceed and asks the user to re-authenticate.

---

## Milestones

### M1: Employee Identity Confirmed

- **Description**: The agent has resolved the requesting user's authenticated session to a valid SuccessFactors employee ID.
- **Achieved when**: A non-null, valid employee ID is obtained from the session context and confirmed against SuccessFactors.
- **Log on achievement**: `M1.achieved: employee identity confirmed, employee_id resolved from session`
- **Log on miss**: `M1.missed: employee identity could not be resolved — session context did not yield a valid employee_id`

### M2: All Data Sections Fetched

- **Description**: The agent has attempted to retrieve all six HR data domains from SuccessFactors Employee Central.
- **Achieved when**: API calls have been made for Personal Information, Employment Information, Skills/Profile, Emergency Contacts/Addresses, and Global Assignments, and responses (including empty/error responses) have been received for all.
- **Log on achievement**: `M2.achieved: all HR data sections fetched — personal_info, employment, skills_profile, emergency_contacts, addresses, global_assignments`
- **Log on miss**: `M2.missed: one or more HR data section retrievals did not complete — sections_attempted=[list], sections_failed=[list]`

### M3: Completeness Check Done

- **Description**: The agent has evaluated each retrieved section against the expected field set and produced a present/missing/partial status for every section.
- **Achieved when**: Completeness check logic has run and a structured status object is available for all six sections.
- **Log on achievement**: `M3.achieved: completeness check completed — complete=[list], partial=[list], missing=[list]`
- **Log on miss**: `M3.missed: completeness check did not complete — reason=[description]`

### M4: Consolidated View Presented

- **Description**: The employee has been shown the unified, structured summary of their full HR record including the completeness status.
- **Achieved when**: The agent has rendered and delivered the consolidated view to the employee in the conversation.
- **Log on achievement**: `M4.achieved: consolidated HR record view presented to employee`
- **Log on miss**: `M4.missed: consolidated view was not presented — reason=[description]`

### M5: Export Delivered

- **Description**: The employee has received their HR record as a downloadable PDF and/or JSON file.
- **Achieved when**: At least one export file (PDF or JSON) has been generated and made available to the employee for download.
- **Log on achievement**: `M5.achieved: export delivered — formats=[pdf|json|both]`
- **Log on miss**: `M5.missed: export was not generated or delivered — formats_requested=[list], reason=[description]`

---

## Risks, Assumptions, and Dependencies

### Risks

- **API availability**: SuccessFactors OData API endpoints may return partial data or errors for certain employee configurations (e.g., employees without global assignments). Mitigated by per-section fallback and graceful degradation.
- **Authentication scoping**: If the BTP session does not reliably expose the employee ID, the agent cannot enforce self-scoping. This is a hard dependency on proper BTP-SuccessFactors SSO configuration.
- **PDF generation complexity**: Rendering a well-structured PDF from dynamic HR data may be complex for records with many sections. A simple but clear layout is preferred over a styled document.

### Assumptions

- The deploying organisation has SAP SuccessFactors Employee Central with the relevant OData APIs enabled.
- BTP-to-SuccessFactors authentication is configured and the employee's session provides a resolvable employee ID.
- All six data domains are activated in the customer's SuccessFactors instance (some may be licensed separately).

### Dependencies

- SAP SuccessFactors Employee Central — OData API access (Personal Information, Employment Information, Skills Management, Employee Profile, Employee Global Information, Global Assignment).
- SAP BTP authentication service for session-based employee ID resolution.

---

## Appendix

### References

- SAP SuccessFactors Employee Central OData API — Personal Information: `sap.sf:apiResource:ECPersonalInformation:v1`
- SAP SuccessFactors Employee Central OData API — Employment Information: `sap.sf:apiResource:ECEmploymentInformation:v1`
- SAP SuccessFactors Employee Central OData API — Skills Management: `sap.sf:apiResource:ECSkillsManagement:v1`
- SAP SuccessFactors Employee Central OData API — Employee Profile: `sap.sf:apiResource:ECEmployeeProfile:v1`
- SAP SuccessFactors Employee Central OData API — Employee Global Information: `sap.sf:apiResource:EmployeeCentralEC:v1`
- SAP SuccessFactors Employee Central OData API — Global Assignment: `sap.sf:apiResource:ECGlobalAssignment:v1`
- SAP Reference Business Architecture — Manage employee information and reporting (BPS-385)
