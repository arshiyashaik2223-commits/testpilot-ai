import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiClient, apiErrorMessage } from "../api/client";
import { FailureAnalysis, GeneratedCode, TestCase, TestRun } from "../types";
import StatusBadge, { toneForPriority, toneForRunStatus } from "../components/StatusBadge";

export default function TestCasePage() {
  const { testCaseId } = useParams<{ testCaseId: string }>();

  const [testCase, setTestCase] = useState<TestCase | null>(null);
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null);
  const [codeDraft, setCodeDraft] = useState("");
  const [runs, setRuns] = useState<TestRun[]>([]);
  const [analyses, setAnalyses] = useState<Record<string, FailureAnalysis>>({});

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isGeneratingCode, setIsGeneratingCode] = useState(false);
  const [isSavingCode, setIsSavingCode] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [analyzingRunId, setAnalyzingRunId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  async function loadAll() {
    setIsLoading(true);
    setError(null);
    try {
      const [testCaseRes, codeRes, runsRes] = await Promise.allSettled([
        apiClient.get(`/api/test-cases/${testCaseId}`),
        apiClient.get(`/api/test-cases/${testCaseId}/code`),
        apiClient.get(`/api/test-cases/${testCaseId}/runs`),
      ]);

      if (testCaseRes.status === "fulfilled") {
        setTestCase(testCaseRes.value.data.test_case);
      } else {
        throw testCaseRes.reason;
      }
      if (codeRes.status === "fulfilled") {
        setGeneratedCode(codeRes.value.data.generated_code);
        setCodeDraft(codeRes.value.data.generated_code.code);
      }
      if (runsRes.status === "fulfilled") {
        setRuns(runsRes.value.data.test_runs);
      } else {
        throw runsRes.reason;
      }
    } catch (err) {
      setError(apiErrorMessage(err, "Could not load this test case."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [testCaseId]);

  async function handleGenerateCode() {
    setActionError(null);
    setIsGeneratingCode(true);
    try {
      const { data } = await apiClient.post(`/api/test-cases/${testCaseId}/generate-code`);
      setGeneratedCode(data.generated_code);
      setCodeDraft(data.generated_code.code);
    } catch (err) {
      setActionError(apiErrorMessage(err, "Code generation failed."));
    } finally {
      setIsGeneratingCode(false);
    }
  }

  async function handleSaveCode() {
    setActionError(null);
    setIsSavingCode(true);
    try {
      const { data } = await apiClient.put(`/api/test-cases/${testCaseId}/code`, {
        code: codeDraft,
      });
      setGeneratedCode(data.generated_code);
    } catch (err) {
      setActionError(apiErrorMessage(err, "Saving code failed."));
    } finally {
      setIsSavingCode(false);
    }
  }

  async function handleExecute() {
    setActionError(null);
    setIsExecuting(true);
    try {
      const { data } = await apiClient.post(`/api/test-cases/${testCaseId}/execute`, {});
      setRuns((prev) => [data.test_run, ...prev]);
    } catch (err) {
      setActionError(apiErrorMessage(err, "Execution failed."));
    } finally {
      setIsExecuting(false);
    }
  }

  async function handleAnalyze(runId: string) {
    setActionError(null);
    setAnalyzingRunId(runId);
    try {
      const { data } = await apiClient.post(`/api/test-runs/${runId}/analyze`);
      setAnalyses((prev) => ({ ...prev, [runId]: data.analysis }));
    } catch (err) {
      setActionError(apiErrorMessage(err, "Failure analysis failed."));
    } finally {
      setAnalyzingRunId(null);
    }
  }

  if (isLoading) return <p className="text-sm text-textMuted">Loading...</p>;
  if (error) return <p className="text-sm text-fail">{error}</p>;

  return (
    <div>
      <Link to="/" className="text-xs text-textMuted hover:text-textPrimary">
        ← Back
      </Link>

      {testCase && (
        <>
          <h1 className="text-xl font-semibold text-textPrimary mt-2">{testCase.scenario}</h1>
          <div className="flex gap-2 mt-2">
            <StatusBadge label={testCase.test_type} tone="accent" />
            <StatusBadge label={testCase.priority} tone={toneForPriority(testCase.priority)} />
          </div>
        </>
      )}

      {/* Code section */}
      <div className="rounded border border-border bg-surface p-5 mt-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-textPrimary">Test code</h2>
          <button
            onClick={handleGenerateCode}
            disabled={isGeneratingCode}
            className="rounded bg-accent text-white text-xs font-medium px-3 py-1.5 hover:bg-accentMuted transition-colors disabled:opacity-50"
          >
            {isGeneratingCode
              ? "Generating..."
              : generatedCode
                ? "Regenerate with AI"
                : "Generate with AI"}
          </button>
        </div>

        {generatedCode ? (
          <>
            <textarea
              value={codeDraft}
              onChange={(e) => setCodeDraft(e.target.value)}
              rows={14}
              spellCheck={false}
              className="w-full rounded border border-border bg-base px-3 py-3 text-xs font-mono text-textPrimary focus:border-accent outline-none resize-y"
            />
            <div className="flex gap-2 mt-3">
              <button
                onClick={handleSaveCode}
                disabled={isSavingCode || codeDraft === generatedCode.code}
                className="rounded border border-border text-textPrimary text-xs font-medium px-3 py-1.5 hover:border-accent transition-colors disabled:opacity-40"
              >
                {isSavingCode ? "Saving..." : "Save changes"}
              </button>
              <button
                onClick={handleExecute}
                disabled={isExecuting || codeDraft !== generatedCode.code}
                title={
                  codeDraft !== generatedCode.code
                    ? "Save your edits before running"
                    : undefined
                }
                className="rounded bg-success/10 border border-success/30 text-success text-xs font-medium px-3 py-1.5 hover:bg-success/20 transition-colors disabled:opacity-40"
              >
                {isExecuting ? "Running..." : "Run test"}
              </button>
            </div>
          </>
        ) : (
          <p className="text-sm text-textMuted">
            No code generated yet — click "Generate with AI" to create a runnable Pytest test
            for this scenario.
          </p>
        )}

        {actionError && <p className="text-sm text-fail mt-3">{actionError}</p>}
      </div>

      {/* Run history */}
      <h2 className="text-sm font-medium text-textPrimary mt-8 mb-3">
        Run history {runs.length > 0 && `(${runs.length})`}
      </h2>

      {runs.length === 0 && (
        <p className="text-sm text-textMuted">No runs yet.</p>
      )}

      <div className="space-y-3">
        {runs.map((run) => {
          const analysis = analyses[run.id];
          const canAnalyze = run.status !== "passed";

          return (
            <div key={run.id} className="rounded border border-border bg-surface p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <StatusBadge label={run.status} tone={toneForRunStatus(run.status)} />
                  <span className="text-xs text-textMuted">
                    {new Date(run.executed_at).toLocaleString()}
                    {run.duration_ms != null && ` · ${run.duration_ms}ms`}
                  </span>
                </div>
                {canAnalyze && !analysis && (
                  <button
                    onClick={() => handleAnalyze(run.id)}
                    disabled={analyzingRunId === run.id}
                    className="rounded border border-accent/40 text-accent text-xs font-medium px-3 py-1.5 hover:bg-accent/10 transition-colors disabled:opacity-50"
                  >
                    {analyzingRunId === run.id ? "Analyzing..." : "Analyze with AI"}
                  </button>
                )}
              </div>

              {run.output && (
                <pre className="mt-3 text-xs font-mono text-textMuted bg-base rounded border border-border p-3 overflow-x-auto max-h-48 whitespace-pre-wrap">
                  {run.output}
                </pre>
              )}

              {analysis && (
                <div className="mt-3 rounded border border-border bg-base p-4 space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <StatusBadge label={analysis.category.replace(/_/g, " ")} tone="accent" />
                    <StatusBadge label={analysis.severity} tone={toneForPriority(analysis.severity)} />
                    <span className="text-xs text-textMuted">
                      {analysis.confidence}% confidence
                    </span>
                  </div>
                  <p className="text-sm text-textPrimary">{analysis.explanation}</p>
                  <p className="text-sm text-textMuted">
                    <span className="text-textPrimary font-medium">Likely cause: </span>
                    {analysis.likely_cause}
                  </p>
                  <p className="text-sm text-textMuted">
                    <span className="text-textPrimary font-medium">Suggested fix: </span>
                    {analysis.suggested_fix}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
