/**
 * MessageBubble Component
 * 
 * PURPOSE:
 * Renders individual chat messages in bubble format with different styling
 * for user vs assistant messages. Think of it as a "message card" that
 * visually distinguishes who said what in the medical conversation.
 * 
 * FUNCTIONALITY:
 * - Displays user messages (right-aligned, blue bubbles)
 * - Displays AI assistant messages (left-aligned, gray bubbles)
 * - Shows error messages with special red styling
 * - Renders medical sources and citations
 * - Displays medical disclaimers for AI responses
 * - Supports Markdown formatting in AI responses
 * - Shows timestamps and user avatars
 * 
 * MEDICAL CONTEXT:
 * Critical for presenting medical information clearly with proper
 * source attribution and safety disclaimers. Ensures users can
 * distinguish between their questions and AI medical guidance.
 * 
 * VISUAL STRUCTURE:
 * [Avatar] [Message Content] [Sources] [Disclaimer]
 * 
 * @component
 * @param {MessageBubbleProps} props - Message data and display options
 * @returns {JSX.Element} Styled message bubble with medical context
 */

import React, { useState } from 'react';
import { Box, Paper, Typography, Avatar, Chip } from '@mui/material';
import { Person, SmartToy, Error as ErrorIcon } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { format } from 'date-fns';
import { MessageBubbleProps } from '../types';
import SourceCitations from './SourceCitations';
import MedicalDisclaimer from './MedicalDisclaimer';
import TypewriterText from './TypewriterText';

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isLastMessage = false }) => {
  const isUser = message.role === 'user';
  const isError = message.isError || false;
  const [typingComplete, setTypingComplete] = useState(!isLastMessage || isUser || isError);

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: isUser ? 'row-reverse' : 'row',
          alignItems: 'flex-start',
          maxWidth: '85%',
          gap: 1,
        }}
      >
        {/* Avatar */}
        <Avatar
          sx={{
            bgcolor: isUser ? 'primary.main' : isError ? 'error.main' : 'secondary.main',
            width: 32,
            height: 32,
            mt: 0.5,
          }}
        >
          {isUser ? (
            <Person fontSize="small" />
          ) : isError ? (
            <ErrorIcon fontSize="small" />
          ) : (
            <SmartToy fontSize="small" />
          )}
        </Avatar>

        {/* Message Content */}
        <Box sx={{ flex: 1 }}>
          <Paper
            elevation={1}
            sx={{
              p: 2,
              bgcolor: isUser 
                ? 'primary.main' 
                : isError 
                ? 'error.light' 
                : 'background.paper',
              color: isUser 
                ? 'primary.contrastText' 
                : isError 
                ? 'error.contrastText' 
                : 'text.primary',
              borderRadius: 2,
              position: 'relative',
            }}
          >
            {/* Message Header */}
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 0.5,
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  opacity: 0.8,
                  fontWeight: 500,
                }}
              >
                {isUser ? 'You' : isError ? 'Error' : 'Medical Assistant'}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  opacity: 0.6,
                  fontSize: '0.75rem',
                }}
              >
                {format(message.timestamp, 'HH:mm')}
              </Typography>
            </Box>

            {/* Message Content */}
            <Box sx={{ '& > *:last-child': { mb: 0 } }}>
              {isUser ? (
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
              ) : isLastMessage && !typingComplete ? (
                <TypewriterText 
                  text={message.content} 
                  speed={20}
                  onComplete={() => setTypingComplete(true)}
                />
              ) : (
                <ReactMarkdown
                  components={{
                    p: ({ children }) => (
                      <Typography variant="body1" sx={{ mb: 1, lineHeight: 1.6 }}>
                        {children}
                      </Typography>
                    ),
                    strong: ({ children }) => (
                      <Typography component="span" sx={{ fontWeight: 600 }}>
                        {children}
                      </Typography>
                    ),
                    em: ({ children }) => (
                      <Typography component="span" sx={{ fontStyle: 'italic' }}>
                        {children}
                      </Typography>
                    ),
                    ul: ({ children }) => (
                      <Box component="ul" sx={{ pl: 2, mb: 1 }}>
                        {children}
                      </Box>
                    ),
                    ol: ({ children }) => (
                      <Box component="ol" sx={{ pl: 2, mb: 1 }}>
                        {children}
                      </Box>
                    ),
                    li: ({ children }) => (
                      <Typography component="li" variant="body1" sx={{ mb: 0.5 }}>
                        {children}
                      </Typography>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              )}
            </Box>

            {/* Status indicator for last message */}
            {isLastMessage && !isUser && !isError && (
              <Chip
                label="Latest"
                size="small"
                color="primary"
                variant="outlined"
                sx={{
                  position: 'absolute',
                  top: -8,
                  right: -8,
                  fontSize: '0.7rem',
                  height: 20,
                }}
              />
            )}
          </Paper>

          {/* Source Citations */}
          {message.sources && message.sources.length > 0 && typingComplete && (
            <Box sx={{ mt: 1 }}>
              <SourceCitations sources={message.sources} />
            </Box>
          )}

          {/* Medical Disclaimer */}
          {message.safetyDisclaimer && typingComplete && (
            <Box sx={{ mt: 1 }}>
              <MedicalDisclaimer disclaimer={message.safetyDisclaimer} />
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default MessageBubble;
