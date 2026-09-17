---
name: hr-record-retrieval
description: Step-by-step instructions for retrieving, consolidating, and presenting an employee's full HR record from SAP SuccessFactors Employee Central, including completeness checking and export guidance.
---

# HR Record Retrieval Skill

## When to Use This Skill

Load this skill when the employee asks to:
- View their HR record or any section of it
- Check what personal, employment, skills, emergency contact, address, or global assignment data is on file
- Download or export their HR record as PDF or JSON

## Step 1 — Identify the Requesting Employee

The requesting employee's identity is always derived from the authenticated session — never ask the employee for their ID.

Use `personIdExternal` or `userId` as available from the session context. All tool calls must filter by this identity.

## Step 2 — Retrieve All HR Data Sections

Retrieve all 6 sections. Where possible, retrieve them in parallel. Each section uses a dedicated MCP tool.

### 2a. Personal Information
- **What to retrieve**: firstName, lastName, dateOfBirth, countryOfBirth, gender, nationality, email, phone
- **Empty response**: Report as "missing" — no personal information on record
- **Partial response**: Report as "partial" — some fields are populated

### 2b. Employment Details
- **What to retrieve**: startDate, jobTitle, department, company, employmentType, emplStatus
- **Empty response**: Report as "missing"
- **Partial response**: Report as "partial"

### 2c. Skills & Profile
- **What to retrieve**: All skills, competencies, and background profile entries
- **Empty response**: Report as "missing" — no skills or profile data on record
- **Any entries returned**: Report as "complete"

### 2d. Emergency Contacts
- **What to retrieve**: All emergency contacts with name, relationship, and phone
- **Empty response**: Report as "missing"
- **At least one contact with name and phone**: Report as "complete"

### 2e. Addresses
- **What to retrieve**: All addresses on file with address1, city, country
- **Empty response**: Report as "missing"
- **At least one address with address1 and city**: Report as "complete"

### 2f. Global Assignments
- **What to retrieve**: All global assignment records
- **Empty response**: Report as "not applicable" — global assignments are optional for all employees
- **Any entries returned**: Report as "complete"

## Step 3 — Completeness Check

After retrieving all sections, assess completeness for each:

| Section | Status Rules |
|---------|-------------|
| Personal Info | **complete** = all 6 core fields present; **partial** = some fields present; **missing** = no data |
| Employment | **complete** = all 6 core fields present; **partial** = some fields present; **missing** = no data |
| Skills & Profile | **complete** = at least 1 entry; **missing** = no entries |
| Emergency Contacts | **complete** = at least 1 contact with name + phone; **partial** = contacts present but incomplete; **missing** = none |
| Addresses | **complete** = at least 1 address with address1 + city; **partial** = addresses present but incomplete; **missing** = none |
| Global Assignments | **complete** = at least 1 assignment; **not applicable** = none (this is normal) |

## Step 4 — Present the Consolidated View

Present the data in a clear, friendly format:

1. Start with a short summary header: "Here is your HR record on file in SuccessFactors:"
2. Show the **Completeness Summary** first — a quick table or list of each section with its status badge
3. Then present each section in order, showing all retrieved fields as label: value pairs
4. Use plain language — avoid technical field names where possible (e.g. "Start Date" not "startDate")
5. For missing sections, clearly say "No [section name] data is currently on record for you."
6. For partial sections, list what is present and note what is missing

### Completeness Badge Format

```
✓ Complete
⚠ Partial — some fields are missing
✗ Missing — no data on record
— Not Applicable
```

## Step 5 — Offer Export

After displaying the record, always offer:

> "Would you like to download your HR record? I can export it as:
> - **PDF** — a formatted document suitable for printing
> - **JSON** — a structured data file for technical use"

## Step 6 — Generate Export on Request

### PDF Export
1. Call the **`generate_hr_pdf`** tool with:
   - `hr_data_json`: serialize ALL collected HR data as a JSON string — include personal_info, employment, skills_profile, emergency_contacts, addresses, and global_assignments
   - `employee_id`: the employee's external person ID (use "unknown" if unavailable)
2. The tool returns a JSON response with `status`, `filename`, and a base64-encoded `data` field
3. Inform the employee: "Your HR record PDF is ready: [filename]"
4. **Never say the tool is unavailable — it is always present.**

### JSON Export
1. Call the **`generate_hr_json`** tool with:
   - `hr_data_json`: serialize ALL collected HR data as a JSON string
   - `employee_id`: the employee's external person ID
2. The tool returns a JSON response with `status`, `filename`, and the export `data` as a string
3. Inform the employee: "Your HR record JSON export is ready: [filename]"
4. **Never say the tool is unavailable — it is always present.**

## Error Handling

| Situation | Action |
|-----------|--------|
| Tool returns error for one section | Report the exact error for that section; continue retrieving other sections |
| All tools fail | Inform the employee that the HR system is temporarily unavailable |
| Session context has no employee ID | Stop and inform: "I could not verify your identity. Please ensure you are logged in." |
| Employee asks for another employee's data | Refuse: "I can only access your own HR data." |

## Important Constraints

- **Read-only only**: Never call any tool that creates, updates, or deletes data
- **Self-scoped only**: All tool calls must be scoped to the requesting employee's ID
- **No fabrication**: Never guess or invent field values — only show what tools return
- **Exact error relay**: If a tool returns an error, report it word-for-word
