export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface Requirement {
  id: string;
  project_id: string;
  text: string;
  created_at: string;
}

export type TestType = "positive" | "negative" | "boundary" | "security" | "validation";
export type Priority = "Low" | "Medium" | "High" | "Critical";

export interface TestCase {
  id: string;
  project_id: string;
  requirement_id: string;
  scenario: string;
  test_type: TestType;
  preconditions: string | null;
  steps: string[];
  test_data: string | null;
  expected_result: string;
  priority: Priority;
  created_at: string;
}

export interface GeneratedCode {
  id: string;
  test_case_id: string;
  code: string;
  created_at: string;
  updated_at: string;
}

export type RunStatus = "passed" | "failed" | "error";

export interface TestRun {
  id: string;
  project_id: string;
  test_case_id: string;
  status: RunStatus;
  output: string | null;
  duration_ms: number | null;
  executed_at: string;
}

export type FailureCategory =
  | "BUG"
  | "ENVIRONMENT_ISSUE"
  | "TEST_SCRIPT_ISSUE"
  | "NETWORK_ISSUE"
  | "DEPENDENCY_ISSUE"
  | "FLAKY_TEST"
  | "PERFORMANCE_ISSUE"
  | "SECURITY_ISSUE";

export interface FailureAnalysis {
  id: string;
  test_run_id: string;
  explanation: string;
  likely_cause: string;
  confidence: number;
  category: FailureCategory;
  severity: Priority;
  suggested_fix: string;
  created_at: string;
}
