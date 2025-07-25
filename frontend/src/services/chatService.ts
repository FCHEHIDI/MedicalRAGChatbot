/**
 * ChatService - Medical RAG API Communication Layer
 * 
 * PURPOSE:
 * Acts as the "translator" between the React frontend and the FastAPI backend.
 * This service handles all communication with the medical RAG system,
 * managing API calls, error handling, and data transformation.
 * 
 * FUNCTIONALITY:
 * - Send medical questions to RAG engine
 * - Receive AI responses with medical sources
 * - Handle conversation history management
 * - Monitor API health and connectivity
 * - Process medical document search requests
 * - Manage error states and retry logic
 * 
 * MEDICAL CONTEXT:
 * Ensures secure and reliable communication for medical data.
 * Handles medical response formatting and source citation delivery.
 * Manages medical disclaimers and safety warnings.
 * 
 * API ENDPOINTS MANAGED:
 * - POST /chat - Send medical questions
 * - GET /health - Check system status  
 * - GET /conversations/{id}/history - Retrieve chat history
 * - DELETE /conversations/{id} - Clear conversation
 * - GET /vector-store/stats - Check medical knowledge base
 * 
 * ERROR HANDLING:
 * - Network connectivity issues
 * - API server downtime
 * - Medical response formatting errors
 * - Authentication and authorization
 * 
 * @service Medical RAG API Communication
 * @author Medical RAG Chatbot Team
 */

import axios, { AxiosResponse } from 'axios';
import {
  ChatRequest,
  ChatResponse,
  HealthCheckResponse,
  ConversationHistory,
  VectorStoreStats,
  ApiError
} from '../types';

// Configure axios defaults
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    // Handle different error scenarios
    if (error.response) {
      // Server responded with error status
      const apiError: ApiError = {
        detail: error.response.data?.detail || 'An error occurred',
        status_code: error.response.status,
      };
      return Promise.reject(apiError);
    } else if (error.request) {
      // Request was made but no response received
      const networkError: ApiError = {
        detail: 'Unable to connect to the server. Please check your internet connection.',
      };
      return Promise.reject(networkError);
    } else {
      // Something else happened
      const unknownError: ApiError = {
        detail: error.message || 'An unexpected error occurred',
      };
      return Promise.reject(unknownError);
    }
  }
);

export const chatService = {
  /**
   * Send a chat message to the medical assistant
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ChatResponse>('/chat', request);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  /**
   * Get health status of the API
   */
  async getHealth(): Promise<HealthCheckResponse> {
    try {
      const response = await apiClient.get<HealthCheckResponse>('/health');
      return response.data;
    } catch (error) {
      console.error('Error getting health status:', error);
      throw error;
    }
  },

  /**
   * Get conversation history
   */
  async getConversationHistory(conversationId: string): Promise<ConversationHistory> {
    try {
      const response = await apiClient.get<ConversationHistory>(
        `/conversations/${conversationId}/history`
      );
      return response.data;
    } catch (error) {
      console.error('Error getting conversation history:', error);
      throw error;
    }
  },

  /**
   * Clear conversation history
   */
  async clearConversation(conversationId: string): Promise<{ message: string; conversation_id: string }> {
    try {
      const response = await apiClient.delete<{ message: string; conversation_id: string }>(
        `/conversations/${conversationId}`
      );
      return response.data;
    } catch (error) {
      console.error('Error clearing conversation:', error);
      throw error;
    }
  },

  /**
   * Get vector store statistics
   */
  async getVectorStoreStats(): Promise<VectorStoreStats> {
    try {
      const response = await apiClient.get<VectorStoreStats>('/vector-store/stats');
      return response.data;
    } catch (error) {
      console.error('Error getting vector store stats:', error);
      throw error;
    }
  },

  /**
   * Get API root information
   */
  async getApiInfo(): Promise<any> {
    try {
      const response = await apiClient.get('/');
      return response.data;
    } catch (error) {
      console.error('Error getting API info:', error);
      throw error;
    }
  },

  /**
   * Test connection to the API
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.getHealth();
      return true;
    } catch (error) {
      return false;
    }
  },
};

export default chatService;
