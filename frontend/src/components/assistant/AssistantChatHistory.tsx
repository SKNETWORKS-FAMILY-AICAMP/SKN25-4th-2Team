import { forwardRef } from "react";

import { renderAssistantContent } from "../../helpers/assistant/renderAssistantContent";
import type { AssistantChatMessage } from "../../types/assistant";

interface AssistantChatHistoryProps {
  messages: AssistantChatMessage[];
  isSending: boolean;
}

export const AssistantChatHistory = forwardRef<
  HTMLDivElement,
  AssistantChatHistoryProps
>(function AssistantChatHistory({ messages, isSending }, ref) {
  return (
    <div className="assistant-chat-history" id="assistant-chat-history" ref={ref}>
      {messages.map((message, index) => {
        if (message.role === "assistant") {
          return (
            <div
              key={`assistant-${index}`}
              className="assistant-message assistant-message-assistant"
              dangerouslySetInnerHTML={{
                __html: renderAssistantContent(message.content),
              }}
            />
          );
        }

        return (
          <div key={`user-${index}`} className="assistant-message assistant-message-user">
            <p>{message.content}</p>
          </div>
        );
      })}

      {isSending ? (
        <div className="assistant-message assistant-message-loading">
          <p>답변을 생성하는 중입니다...</p>
        </div>
      ) : null}
    </div>
  );
});
