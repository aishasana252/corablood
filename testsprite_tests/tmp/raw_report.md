
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** CoraBlood-Ultimat-main
- **Date:** 2026-04-13
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001 postportalregisternewdonor
- **Test Code:** [TC001_postportalregisternewdonor.py](./TC001_postportalregisternewdonor.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 38, in <module>
  File "<string>", line 28, in test_postportalregisternewdonor
AssertionError: Expected status 200 or 302 but got 400

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/a96afe14-d421-4477-9bd8-9ff2a80e5504
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002 postportalloginvaliddonorcredentials
- **Test Code:** [TC002_postportalloginvaliddonorcredentials.py](./TC002_postportalloginvaliddonorcredentials.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 51, in <module>
  File "<string>", line 27, in test_postportalloginvaliddonorcredentials
AssertionError: Unexpected registration status code: 400

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/01407a3b-fe47-466e-a80d-9a5288a2ae05
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003 postportalregisterduplicateemail
- **Test Code:** [TC003_postportalregisterduplicateemail.py](./TC003_postportalregisterduplicateemail.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 52, in <module>
  File "<string>", line 23, in test_postportalregisterduplicateemail
AssertionError: Initial registration failed: 400 {"error": "Missing required fields for JSON registration."}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/f82810c2-1ee6-4558-9cbe-8aadcda00a49
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004 postportallogininvalidcredentials
- **Test Code:** [TC004_postportallogininvalidcredentials.py](./TC004_postportallogininvalidcredentials.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/97f3cd95-a9aa-4a3b-b985-692739ea8822
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005 postportaldashboardbookappointment
- **Test Code:** [TC005_postportaldashboardbookappointment.py](./TC005_postportaldashboardbookappointment.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 94, in <module>
  File "<string>", line 33, in test_postportaldashboardbookappointment
AssertionError: Registration failed: 400, {"error": "Missing required fields for JSON registration."}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/c42150e7-02fc-4f08-b9c3-77d8eb258185
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006 postportaldashboardconflictingappointmenttime
- **Test Code:** [TC006_postportaldashboardconflictingappointmenttime.py](./TC006_postportaldashboardconflictingappointmenttime.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 69, in <module>
  File "<string>", line 22, in test_postportaldashboardconflictingappointmenttime
AssertionError: Registration failed: {"error": "Missing required fields for JSON registration."}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/39f901e1-be54-4d98-b844-ea0579f116dd
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007 postportalquestionnairesubmitwithsignature
- **Test Code:** [TC007_postportalquestionnairesubmitwithsignature.py](./TC007_postportalquestionnairesubmitwithsignature.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 79, in <module>
  File "<string>", line 27, in test_post_portal_questionnaire_submit_with_signature
AssertionError: Registration failed: 400 {"error": "Missing required fields for JSON registration."}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/6289629b-56d6-4226-9497-7284096e7267
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008 postportalquestionnairemissingsignature
- **Test Code:** [TC008_postportalquestionnairemissingsignature.py](./TC008_postportalquestionnairemissingsignature.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 59, in <module>
  File "<string>", line 22, in test_postportalquestionnairemissingsignature
AssertionError: Unexpected register status: 400

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/a6466dc8-4983-44d1-be6a-25a1f16340e5
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009 postportalmedicationsubmitvalid
- **Test Code:** [TC009_postportalmedicationsubmitvalid.py](./TC009_postportalmedicationsubmitvalid.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 61, in <module>
  File "<string>", line 20, in postportalmedicationsubmitvalid
AssertionError: Registration failed with status 400

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/e5332472-e765-4d9a-857a-b297b4ae1bfd
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010 getapidonationsfetchworkflowadmin
- **Test Code:** [TC010_getapidonationsfetchworkflowadmin.py](./TC010_getapidonationsfetchworkflowadmin.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 156, in <module>
  File "<string>", line 21, in test_get_api_donations_fetch_workflow_admin
AssertionError: Admin login failed with status 401

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/1c349fa4-71b2-4f64-a03b-aa1467a37574/71055ab7-6e48-49de-be71-f5618e740dbd
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **10.00** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---