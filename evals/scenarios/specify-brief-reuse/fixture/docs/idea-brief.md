---
status: Draft
owner: Maintainer
updated_at: "2026-09-17"
depth: medium
---
# Idea brief — export-status
## 1. Raw idea
Our on-call engineers cannot tell whether yesterday's exports finished. We already use PostgreSQL. I want one place to see the last outcome; no new notification service.
## 2. Problem
owner-reported: on-call engineers cannot distinguish failed and late-completed exports before deciding what to investigate. Desired result: see the recorded outcome.
## 3. Users
On-call operators already authorized for their own tenant; no new audience.
## 4. Why now
owner-reported: repeated support confusion; no numeric frequency or deadline established.
## 5. Out of scope
Owner-accepted: no rerun controls, cross-tenant access, new roles, notifications, or new service. Preserve PostgreSQL and existing tenant isolation.
## 6. Risks
owner-reported: records exist; confirm read-path implementation during design. No live runtime proof yet. No independent critique was claimed.
## 7. Recommendation
Owner-accepted: read-only visibility into existing export outcomes for authorized on-call operators. Rejected: notifications and rerun controls because they expand scope.
Outcome: ready-for-specify. Specify observable behavior; design must inspect actual records and preserve access.
## 8. Open questions
Nonblocking for specification: locate the current outcome read path during design; owner Maintainer. No remaining owner-intent blockers.
