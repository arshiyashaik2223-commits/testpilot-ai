import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiClient, apiErrorMessage } from "../api/client";
import { Project } from "../types";

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function loadProjects() {
    setIsLoading(true);
    setError(null);
    try {
      const { data } = await apiClient.get("/api/projects");
      setProjects(data.projects);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not load projects."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadProjects();
  }, []);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setFormError(null);
    setIsCreating(true);
    try {
      await apiClient.post("/api/projects", { name, description });
      setName("");
      setDescription("");
      setShowForm(false);
      await loadProjects();
    } catch (err) {
      setFormError(apiErrorMessage(err, "Could not create project."));
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-textPrimary">Projects</h1>
          <p className="text-sm text-textMuted mt-1">
            Each project holds its own requirements, test cases, and results.
          </p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded bg-accent text-white text-sm font-medium px-4 py-2 hover:bg-accentMuted transition-colors"
        >
          New project
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-6 rounded border border-border bg-surface p-5 space-y-3"
        >
          <div>
            <label className="block text-xs text-textMuted mb-1.5" htmlFor="project-name">
              Project name
            </label>
            <input
              id="project-name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Checkout API"
              className="w-full rounded border border-border bg-base px-3 py-2 text-sm text-textPrimary focus:border-accent outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-textMuted mb-1.5" htmlFor="project-description">
              Description (optional)
            </label>
            <textarea
              id="project-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="w-full rounded border border-border bg-base px-3 py-2 text-sm text-textPrimary focus:border-accent outline-none resize-none"
            />
          </div>
          {formError && <p className="text-sm text-fail">{formError}</p>}
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isCreating}
              className="rounded bg-accent text-white text-sm font-medium px-4 py-2 hover:bg-accentMuted transition-colors disabled:opacity-50"
            >
              {isCreating ? "Creating..." : "Create project"}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="rounded text-sm text-textMuted px-4 py-2 hover:text-textPrimary transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {isLoading && <p className="text-sm text-textMuted">Loading projects...</p>}
      {error && <p className="text-sm text-fail">{error}</p>}

      {!isLoading && !error && projects.length === 0 && (
        <div className="rounded border border-dashed border-border p-8 text-center">
          <p className="text-sm text-textMuted">
            No projects yet. Create one to start generating test cases.
          </p>
        </div>
      )}

      <div className="space-y-2">
        {projects.map((project) => (
          <Link
            key={project.id}
            to={`/projects/${project.id}`}
            className="block rounded border border-border bg-surface px-5 py-4 hover:border-accent/50 transition-colors"
          >
            <p className="text-sm font-medium text-textPrimary">{project.name}</p>
            {project.description && (
              <p className="text-sm text-textMuted mt-1">{project.description}</p>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
