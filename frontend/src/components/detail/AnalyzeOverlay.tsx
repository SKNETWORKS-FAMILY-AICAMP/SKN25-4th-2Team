interface AnalyzeOverlayProps {
  title: string;
  message: string;
  visible: boolean;
}

export function AnalyzeOverlay({ title, message, visible }: AnalyzeOverlayProps) {
  if (!visible) {
    return null;
  }

  return (
    <div id="analyze-overlay">
      <div className="overlay-title">{title}</div>
      <div className="overlay-msg">{message}</div>
      <div className="big-spinner" />
    </div>
  );
}
