import type { KeyboardEvent, RefObject } from "react";

interface AssistantComposerProps {
  value: string;
  disabled: boolean;
  inputRef?: RefObject<HTMLInputElement>;
  onChange: (nextValue: string) => void;
  onSend: () => void;
}

export function AssistantComposer({
  value,
  disabled,
  inputRef,
  onChange,
  onSend,
}: AssistantComposerProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    onSend();
  };

  return (
    <div className="assistant-composer">
      <input
        id="assistant-chat-input"
        type="text"
        placeholder="Ask about trends, papers, or a research topic"
        ref={inputRef}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <button id="assistant-send-btn" onClick={onSend} disabled={disabled}>
        Send
      </button>
    </div>
  );
}
