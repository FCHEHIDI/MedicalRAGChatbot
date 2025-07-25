/**
 * ChatInterface Component
 * 
 * PURPOSE:
 * Main container component that orchestrates the entire chat experience.
 * This is the "conductor" of the medical conversation - it manages the flow
 * between user input, message display, and system responses.
 * 
 * FUNCTIONALITY:
 * - Displays conversation history in scrollable message bubbles
 * - Handles user input through ChatInput component
 * - Shows typing indicators during AI processing
 * - Manages conversation state and message flow
 * - Auto-scrolls to newest messages for better UX
 * 
 * MEDICAL CONTEXT:
 * This component ensures medical conversations are presented clearly
 * with proper source citations and medical disclaimers visible.
 * 
 * DATA FLOW:
 * User Input → ChatInput → ChatInterface → App.tsx → API → Response → MessageBubble
 * 
 * @component
 * @param {ChatInterfaceProps} props - Interface properties for chat management
 * @returns {JSX.Element} Complete chat interface with messages and input
 */

import React, { useRef, useEffect } from 'react';
import { Box, Divider } from '@mui/material';
import { ChatInterfaceProps } from '../types';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onClearConversation,
  disabled = false,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = (message: string) => {
    if (!disabled && !isLoading) {
      onSendMessage(message);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Messages Container */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          bgcolor: '#fafafa',
        }}
      >
        {messages.length === 0 && !isLoading && (
          <Box
            sx={{
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'text.secondary',
              textAlign: 'center',
            }}
          >
            <div>
              <h3>👋 Welcome to your AI Medical Assistant</h3>
              <p>
                Ask me any medical question and I'll provide evidence-based information
                <br />
                with citations from reliable medical sources.
              </p>
              <p style={{ fontSize: '0.9em', marginTop: '20px' }}>
                <strong>Example questions:</strong>
                <br />
                • "What are the symptoms of hypertension?"
                <br />
                • "How is type 2 diabetes managed?"
                <br />
                • "What should I know about chest pain evaluation?"
              </p>
            </div>
          </Box>
        )}

        {messages.map((message, index) => (
          <MessageBubble
            key={message.id}
            message={message}
            isLastMessage={index === messages.length - 1}
          />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </Box>

      <Divider />

      {/* Chat Input */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        disabled={disabled}
        onClearConversation={onClearConversation}
      />
    </Box>
  );
};

export default ChatInterface;
