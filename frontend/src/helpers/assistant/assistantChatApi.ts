import type {
  AssistantChatRequest,
  AssistantChatResponse,
} from "../../types/assistant";
import { fetchJsonWithBody } from "../http";

export interface PostAssistantChatParams extends AssistantChatRequest {
  endpoint: string;
}

export async function postAssistantChat({
  endpoint,
  message,
  history,
}: PostAssistantChatParams): Promise<AssistantChatResponse> {
  return fetchJsonWithBody<AssistantChatResponse>(endpoint, "POST", { message, history });
}
