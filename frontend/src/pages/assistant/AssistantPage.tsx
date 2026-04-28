import { useEffect, useRef, useState } from "react";

import { AssistantChatHistory } from "../../components/assistant/AssistantChatHistory";
import { AssistantComposer } from "../../components/assistant/AssistantComposer";
import { AssistantHero } from "../../components/assistant/AssistantHero";
import { AssistantNotice } from "../../components/assistant/AssistantNotice";
import { postAssistantChat } from "../../helpers/assistant/assistantChatApi";
import type {
  AssistantChatMessage,
  AssistantChatResponse,
} from "../../types/assistant";
import type { BootstrapPayload } from "../../types/app";
import "./assistant-page.css";

const INITIAL_ASSISTANT_MESSAGE =
  "찾고 싶은 연구 주제나 기술 키워드를 질문해 주세요.";
const FALLBACK_ERROR_MESSAGE = "답변을 불러오는 중 오류가 발생했습니다.";

export interface AssistantPageProps {
  session: BootstrapPayload;
  initialQuery?: string;
  assistantChatEndpoint?: string;
  homeHref?: string;
  onRequireLogin: () => void;
  onOpenSettings: () => void;
}

export function AssistantPage({
  session,
  initialQuery = "",
  assistantChatEndpoint = "/papers/assistant/chat/",
  homeHref = "/",
  onRequireLogin,
  onOpenSettings,
}: AssistantPageProps) {
  const [messages, setMessages] = useState<AssistantChatMessage[]>([
    { role: "assistant", content: INITIAL_ASSISTANT_MESSAGE },
  ]);
  const [chatHistory, setChatHistory] = useState<AssistantChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isSending, setIsSending] = useState(false);
  const hasSubmittedInitialQueryRef = useRef(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  const canUseAssistant = session.is_authenticated && session.has_personal_api_key;

  const scrollToBottom = () => {
    if (!chatHistoryRef.current) {
      return;
    }
    chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const sendMessage = async (prefilledMessage = "") => {
    if (!canUseAssistant || isSending) {
      return;
    }

    const message = (prefilledMessage || inputValue).trim();
    if (!message) {
      return;
    }

    const requestHistory = chatHistory;
    const userMessage: AssistantChatMessage = { role: "user", content: message };

    setInputValue("");
    setIsSending(true);
    setMessages((previous) => [...previous, userMessage]);
    setChatHistory((previous) => [...previous, userMessage]);

    try {
      const data: AssistantChatResponse = await postAssistantChat({
        endpoint: assistantChatEndpoint,
        message,
        history: requestHistory,
      });
      const answer = data.error ? `오류: ${data.error}` : data.answer || "";
      const assistantMessage: AssistantChatMessage = {
        role: "assistant",
        content: answer,
      };
      setMessages((previous) => [...previous, assistantMessage]);
      setChatHistory((previous) => [...previous, assistantMessage]);
    } catch (error) {
      const assistantMessage: AssistantChatMessage = {
        role: "assistant",
        content: FALLBACK_ERROR_MESSAGE,
      };
      setMessages((previous) => [...previous, assistantMessage]);
    } finally {
      setIsSending(false);
      inputRef.current?.focus();
    }
  };

  useEffect(() => {
    if (!canUseAssistant || !initialQuery.trim() || hasSubmittedInitialQueryRef.current) {
      return;
    }
    hasSubmittedInitialQueryRef.current = true;
    void sendMessage(initialQuery.trim());
  }, [canUseAssistant, initialQuery]);

  return (
    <main className="assistant-page">
      <div className="assistant-page-inner">
        <AssistantHero />
        {canUseAssistant ? null : (
          <AssistantNotice
            isAuthenticated={session.is_authenticated}
            homeHref={homeHref}
            onRequireLogin={onRequireLogin}
            onOpenSettings={onOpenSettings}
          />
        )}

        <div className="assistant-chat-shell">
          <AssistantChatHistory messages={messages} isSending={isSending} ref={chatHistoryRef} />
          <AssistantComposer
            value={inputValue}
            disabled={!canUseAssistant || isSending}
            inputRef={inputRef}
            onChange={setInputValue}
            onSend={() => {
              void sendMessage();
            }}
          />
        </div>
      </div>
    </main>
  );
}
