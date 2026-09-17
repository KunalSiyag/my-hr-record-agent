# My HR Record Agent

Employee self-service AI agent for consolidated HR data view and export from SAP SuccessFactors Employee Central

## Business challenge

Employees have no single, self-serve way to retrieve a complete, consolidated view of all the HR data held about them in SuccessFactors Employee Central. Retrieving personal information, employment details, skills, emergency contacts, home addresses, and global assignments currently requires manual HR involvement or navigating multiple screens. The agent must gather all sections, clearly flag anything missing, and offer a downloadable export — operating strictly on the requesting employee's own record in a read-only manner.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| HR data fields coverage | — | 100% of fields returned with no gaps | — | Employee self-service HR record retrieval | user |
| Manual HR team involvement for data requests | — | 0 interventions per request | — | Employee Administration (SuccessFactors) | user |
| Data consistency across sections | — | Zero discrepancies between sections | — | Employee information & reporting | user |

## Key Milestones

| Milestone | Condition |
|-----------|-----------|
| Employee identity confirmed | Agent resolves the requesting user's employee ID from the session context |
| All data sections fetched | Agent has queried Personal Info, Employment, Skills/Profile, Emergency Contacts, Addresses, and Global Assignments from SuccessFactors EC |
| Completeness check done | Agent has evaluated each section and produced a clear present/missing status for every field group |
| Consolidated view presented | Employee sees a unified, structured summary of their full HR record in the conversation |
| Export delivered | Employee receives their record as both a PDF and a JSON file on request |

## Business Architecture (RBA)

### End-to-End Process

Recruit to Retire

### Process Hierarchy

```
Recruit to Retire
└── Manage Workforce (generic)
    └── Manage employee information and reporting (generic) (BPS-385)
        └── Manage employment and assignment data
        └── Manage workforce data
```

### Summary

The agent maps to the "Manage Workforce" phase of Recruit to Retire, specifically the "Manage employee information and reporting" sub-process (BPS-385). It delivers an employee-facing, read-only self-service capability over SuccessFactors Employee Central data, covering all workforce data domains.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|------|---------------------|
| Retrieve personal information | SAP SuccessFactors Employee Central — Employee Administration (SC1251) | `sap.sf:apiResource:ECPersonalInformation:v1` | — | — | No | OData API available; no MCP server — agent calls API directly |
| Retrieve employment details | SAP SuccessFactors Employee Central — Employee Administration (SC1251) | `sap.sf:apiResource:ECEmploymentInformation:v1` | — | — | No | OData API available; no MCP server — agent calls API directly |
| Retrieve skills and profile | SAP SuccessFactors Employee Central — Employee Administration (SC1251) | `sap.sf:apiResource:ECSkillsManagement:v1`, `sap.sf:apiResource:ECEmployeeProfile:v1` | — | — | No | OData APIs available; no MCP server — agent calls APIs directly |
| Retrieve emergency contacts and addresses | SAP SuccessFactors Employee Central — Employee Administration (SC1251) | `sap.sf:apiResource:EmployeeCentralEC:v1` | — | — | No | Employee Global Information OData API covers contacts and addresses |
| Retrieve global assignments | SAP SuccessFactors Employee Central — Global Assignment Management (SC1259) | `sap.sf:apiResource:ECGlobalAssignment:v1` | — | — | No | OData API available; no MCP server — agent calls API directly |
| Export as PDF and JSON | Custom | — | — | — | Yes | No standard SAP export covers both formats; agent generates exports using custom rendering logic |
| Completeness/missing-field detection | Custom | — | — | — | Yes | No standard capability; agent logic must compare fetched data against expected field set and flag gaps |

### Key findings
- SAP SuccessFactors Employee Central provides full OData API coverage for all required HR data domains (personal info, employment, skills, profile, emergency contacts, addresses, global assignments).
- No MCP servers are currently available for any of these SuccessFactors APIs — the agent will call the OData APIs directly using tool wrappers built from the API specs.
- The Compound Employee API (SOAP) can serve as a fallback to retrieve multiple data blocks in a single call.
- Two genuine gaps exist: dual-format export (PDF + JSON) and completeness detection logic — both require custom implementation within the agent.
- The solution must enforce strict self-service scoping — the agent must only read data for the authenticated requesting employee and must never allow cross-employee access.
- SAP SuccessFactors Employee Central is the single source of truth; no additional HR systems need to be integrated.

## Recommendations

### My HR Record AI Agent

#### Executive Summary

Read-only Python AI agent that consolidates all SuccessFactors EC data into one view with PDF/JSON export.

#### Recommended Solution

A pro-code Python AI agent (A2A protocol) that connects to SAP SuccessFactors Employee Central via its OData APIs. On request, the agent fetches the employee's personal information, employment details, skills and profile, emergency contacts, home addresses, and global assignments, assembles them into a single consolidated view, flags any missing or empty sections, and generates a PDF and/or JSON export for the employee. The agent is strictly read-only and operates only on the authenticated employee's own record.

MCP translation files will be generated from the SuccessFactors OData API specs to expose the data retrieval operations as agent tools.

#### Recommended solution category

AI Agent

#### Intent fit
95%
