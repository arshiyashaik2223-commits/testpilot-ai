interface StatusBadgeProps {
  label: string;
  tone: "success" | "fail" | "warning" | "neutral" | "accent";
}

const TONE_CLASSES: Record<StatusBadgeProps["tone"], string> = {
  success: "bg-success/10 text-success border-success/30",
  fail: "bg-fail/10 text-fail border-fail/30",
  warning: "bg-warning/10 text-warning border-warning/30",
  neutral: "bg-surfaceRaised text-textMuted border-border",
  accent: "bg-accent/10 text-accent border-accent/30",
};

export default function StatusBadge({ label, tone }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded border px-2 py-0.5 text-xs font-medium ${TONE_CLASSES[tone]}`}
    >
      {label}
    </span>
  );
}

export function toneForRunStatus(status: string): StatusBadgeProps["tone"] {
  if (status === "passed") return "success";
  if (status === "failed") return "fail";
  return "warning"; // "error"
}

export function toneForPriority(priority: string): StatusBadgeProps["tone"] {
  if (priority === "Critical" || priority === "High") return "fail";
  if (priority === "Medium") return "warning";
  return "neutral";
}
