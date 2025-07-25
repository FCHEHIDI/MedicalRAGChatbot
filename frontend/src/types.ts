/**
 * TypeScript Type Definitions for Medical RAG Chatbot
 * 
 * PURPOSE:
 * This file serves as the "CSS for data types" - it defines the exact
 * structure and rules for all data flowing through the medical application.
 * Just like CSS styles visual elements, these types style data elements.
 * 
 * MEDICAL CONTEXT:
 * Type safety is critical in medical applications. These definitions ensure
 * that medical data, responses, sources, and user interactions are always
 * structured correctly, preventing data corruption that could affect
 * medical advice accuracy.
 * 
 * BIDIRECTIONAL VALIDATION:
 * These types validate data both:
 * - INPUT: Going from frontend to backend (user questions, requests)
 * - OUTPUT: Coming from backend to frontend (AI responses, medical sources)
 * 
 * ANALOGY:
 * If CSS defines: .button { color: blue; padding: 10px; }
 * Then TypeScript defines: Message { role: 'user'; content: string; }
 * 
 * @fileoverview Medical RAG Chatbot TypeScript definitions
 * @author Medical RAG Development Team
 */

// TypeScript type definitions for the Medical RAG Chatbot

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: SourceCitation[];
  safetyDisclaimer?: string;
  isError?: boolean;
}

export interface SourceCitation {
  title: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  include_sources?: boolean;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: SourceCitation[];
  safety_disclaimer: string;
  timestamp: string;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  version: string;
  components: Record<string, string>;
}

export interface ConversationHistory {
  conversation_id: string;
  history: {
    role: string;
    content: string;
    timestamp: string;
    sources?: SourceCitation[];
  }[];
}

export interface VectorStoreStats {
  status: string;
  total_vectors?: number;
  dimension?: number;
  index_fullness?: number;
  namespaces?: Record<string, any>;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string) => Promise<void>;
  onClearConversation: () => Promise<void>;
  disabled?: boolean;
}

export interface MessageBubbleProps {
  message: Message;
  isLastMessage?: boolean;
}

export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
  onClearConversation?: () => Promise<void>;
}

export interface SourceCitationsProps {
  sources: SourceCitation[];
}

export interface MedicalDisclaimerProps {
  disclaimer: string;
}
