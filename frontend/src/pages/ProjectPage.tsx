import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiClient, apiErrorMessage } from "../api/client";
import { Project, TestCase } from "../types";
import StatusBadge, { toneForPriority } from "../components/StatusBadge";

const TEST_TYPE_TONE: Record<string, "accent" | "fail" | "warning" | "neutral"> = {
  positive: "accent",
  negative: "warning",
  boundary: "neutral",
  security: "fail",
  validation: "neutral",
};

export default function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();

  const [project, setProject] = useState<Project | null>(null);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [requirementText, setRequirementText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);

  async function loadProjectData() {
    setIsLoading(true);
    setError(null);
    try {
      const [projectRes, testCasesRes] = await Promise.all([
        apiClient.get(`/api/projects/${projectId}`),
        apiClient.get(`/api/projects/${projectId}/test-cases`),
      ]);
      setProject(projectRes.data.project);
      setTestCases(testCasesRes.data.test_cases);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not load this project."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadProjectData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  async function handleGenerate(e: FormEvent) {
    e.preventDefault();
    setGenerateError(null);
    setIsGenerating(true);
    try {
      await apiClient.post(`/api/projects/${projectId}/requirements`, {
        text: requirementText,
      });
      setRequirementText("");
      await loadProjectData();
    } catch (err) {
      setGenerateError(apiErrorMessage(err, "Test case generation failed."));
    } finally {
      setIsGenerating(false);
    }
  }

  if (isLoading) return <p className="text-sm text-textMuted">Loading...</p>;
  if (error) return <p className="text-sm text-fail">{error}</p>;
  if (!project) return null;

  return (
    <div>
      <Link to="/" className="text-xs text-textMuted hover:text-textPrimary">
        ← Projects
      </Link>
      <h1 className="text-xl font-semibold text-textPrimary mt-2">{project.name}</h1>
      {project.description && (
        <p className="text-sm text-textMuted mt-1">{project.description}</p>
      )}

      <div className="rounded border border-border bg-surface p-5 mt-6">
        <h2 className="text-sm font-medium text-textPrimary mb-1">Generate test cases</h2>
        <p className="text-xs text-textMuted mb-3">
          Describe a requirement in plain English. AI will generate positive, negative,
          boundary, validation, and security test cases from it.
        </p>
        <form onSubmit={handleGenerate}>
          <textarea
            required
            value={requirementText}
            onChange={(e) => setRequirementText(e.target.value)}
            rows={3}
            placeholder="e.g. User should be able to register using email and password."
            className="w-full rounded border border-border bg-base px-3 py-2 text-sm text-textPrimary focus:border-accent outline-none resize-none"
          />
          {generateError && <p className="text-sm text-fail mt-2">{generateError}</p>}
          <button
            type="submit"
            disabled={isGenerating}
            className="mt-3 rounded bg-accent text-white text-sm font-medium px-4 py-2 hover:bg-accentMuted transition-colors disabled:opacity-50"
          >
            {isGenerating ? "Generating test cases..." : "Generate test cases"}
          </button>
        </form>
      </div>

      <h2 className="text-sm font-medium text-textPrimary mt-8 mb-3">
        Test cases {testCases.length > 0 && `(${testCases.length})`}
      </h2>

      {testCases.length === 0 && (
        <div className="rounded border border-dashed border-border p-8 text-center">
          <p className="text-sm text-textMuted">
            No test cases yet. Generate some from a requirement above.
          </p>
        </div>
      )}

      <div className="space-y-2">
        {testCases.map((tc) => (
          <Link
            key={tc.id}
            to={`/test-cases/${tc.id}`}
            className="block rounded border border-border bg-surface px-5 py-4 hover:border-accent/50 transition-colors"
          >
            <div className="flex items-start justify-between gap-4">
              <p className="text-sm font-medium text-textPrimary">{tc.scenario}</p>
              <div className="flex gap-2 shrink-0">
                <StatusBadge label={tc.test_type} tone={TEST_TYPE_TONE[tc.test_type] || "neutral"} />
                <StatusBadge label={tc.priority} tone={toneForPriority(tc.priority)} />
              </div>
            </div>
            <p className="text-xs text-textMuted mt-1.5">{tc.expected_result}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
