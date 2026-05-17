# smart-issue-triage


## 1. Updated Relational Table Layout

### Table A: `employees` (The Profile Master)

Stores static background information for corporate identities.

| Column Name        | Data Type      | Constraints / Properties      | Dummy Example            |
| ------------------ | -------------- | ----------------------------- | ------------------------ |
| `employee_id`      | `VARCHAR(50)`  | **Primary Key**, `NOT NULL`   | `'USR_9821'`             |
| `employee_name`    | `VARCHAR(100)` | `NOT NULL`                    | `'Alice Smith'`          |
| `email`            | `VARCHAR(100)` | `UNIQUE`, `NOT NULL`          | `'alice.smith@corp.com'` |
| `phone_number`     | `VARCHAR(15)`  | `NOT NULL`                    | `'555-0199'`             |
| `department_group` | `VARCHAR(50)`  | Default: `'Internal Support'` | `'Finance IT'`           |
| `default_location` | `VARCHAR(50)`  | `NOT NULL`                    | `'HQ - Building A'`      |

---

### Table B: `tickets` (The Core Ledger - Cleaned)

This table now holds **only** the unchanging core facts of what the issue is, what category it belongs to, and who raised it. The status metrics have been completely removed.

| Column Name          | Data Type      | Constraints / Properties                            | Dummy Example                                                    |
| -------------------- | -------------- | --------------------------------------------------- | ---------------------------------------------------------------- |
| `ticket_id`          | `SERIAL`       | **Primary Key**                                     | `1001`                                                           |
| `employee_id`        | `VARCHAR(50)`  | **Foreign Key** `REFERENCES employees(employee_id)` | `'USR_9821'`                                                     |
| `specific_facility`  | `VARCHAR(100)` | `NOT NULL`                                          | `'Floor 3 - Bay B'`                                              |
| `catalog_category`   | `VARCHAR(50)`  | `NOT NULL`                                          | `'Facility Services'`                                            |
| `catalog_item`       | `VARCHAR(50)`  | `NOT NULL`                                          | `'Temperature Control'`                                          |
| `request_sub_type`   | `VARCHAR(100)` | Nullable                                            | `'AC Leaking'`                                                   |
| `ticket_description` | `TEXT`         | `NOT NULL`                                          | `'The office AC unit is dripping water onto workspace desk 14.'` |
| `callback_consent`   | `BOOLEAN`      | Default: `TRUE`                                     | `True`                                                           |
| `resolution_summary` | `TEXT`         | Nullable                                            | *[Filled on closure to feed the MCP vector store]*               |
| `created_at`         | `TIMESTAMP`    | Default: `CURRENT_TIMESTAMP`                        | `2026-05-17 14:00:00`                                            |

---

### Table C: `ticket_status_history` (The New Tracking Ledger)

Every time a ticket changes states (e.g., from Draft ➡️ Open ➡️ Escalated ➡️ Resolved), a **new row** is appended here. To find the current state of any ticket, you simply fetch the most recent entry for that `ticket_id`.

| Column Name       | Data Type     | Constraints / Properties                        | Dummy Example                                                                     | Purpose                                                                |
| ----------------- | ------------- | ----------------------------------------------- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `status_entry_id` | `SERIAL`      | **Primary Key**                                 | `5001`                                                                            | Unique tracking row index.                                             |
| `ticket_id`       | `INT`         | **Foreign Key** `REFERENCES tickets(ticket_id)` | `1001`                                                                            | Links directly back to the core issue.                                 |
| `status`          | `VARCHAR(30)` | `NOT NULL`                                      | `'Escalated_To_Human'`                                                            | The workflow state (`Draft`, `Open`, `In_Progress`, `Resolved`).       |
| `assigned_owner`  | `VARCHAR(50)` | `NOT NULL`                                      | `'Human_Queue_Tier_1'`                                                            | Who currently holds responsibility (`AI_Agent` or an actual agent id). |
| `assigned_at`     | `TIMESTAMP`   | Default: `CURRENT_TIMESTAMP`                    | `2026-05-17 14:15:30`                                                             | **Exact timeline clock when this specific step began.**                |
| `status_notes`    | `TEXT`        | Nullable                                        | `'AI chatbot failed evaluation check; handing off with chat transcript history.'` | Explains *why* the state transitioned.                                 |

---