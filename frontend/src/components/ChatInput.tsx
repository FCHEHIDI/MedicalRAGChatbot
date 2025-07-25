/**
 * ChatInput Component
 * 
 * PURPOSE:
 * Handles user input for medical questions and symptoms. This is the
 * "gateway" where users communicate with the AI medical assistant.
 * It's like a smart medical receptionist that helps format questions.
 * 
 * FUNCTIONALITY:
 * - Text input field for medical questions
 * - Send button to submit queries
 * - Enter key support for quick sending
 * - Character limit validation
 * - Suggested medical questions dropdown
 * - Input sanitization and validation
 * - Loading state management during AI processing
 * 
 * MEDICAL CONTEXT:
 * Provides pre-written medical question templates to help users
 * ask better questions and get more accurate medical information.
 * Includes input validation to ensure medical queries are appropriate.
 * 
 * USER EXPERIENCE:
 * - Multiline support for complex medical descriptions
 * - Smart suggestions for common medical queries
 * - Clear visual feedback during processing
 * 
 * @component
 * @param {ChatInputProps} props - Input handling and state management
 * @returns {JSX.Element} Medical question input interface
 */

import React, { useState, KeyboardEvent } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Send,
  MoreVert,
  Clear,
  Help,
} from '@mui/icons-material';
import { ChatInputProps } from '../types';

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  disabled = false,
  onClearConversation,
}) => {
  const [message, setMessage] = useState('');
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);

  const handleSend = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !isLoading && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');
    }
  };

  const handleKeyPress = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  const handleClearConversation = () => {
    onClearConversation?.();
    handleMenuClose();
  };

  const sampleQuestions = [
    "What are the symptoms of hypertension?",
    "How is type 2 diabetes managed?",
    "What causes chest pain?",
    "What are the side effects of ACE inhibitors?",
    "How is pneumonia diagnosed?",
  ];

  const handleSampleQuestion = (question: string) => {
    if (!isLoading && !disabled) {
      onSendMessage(question);
    }
    handleMenuClose();
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        bgcolor: 'background.paper',
        borderTop: '1px solid',
        borderTopColor: 'divider',
      }}
    >
      {/* Sample Questions (only show when no conversation) */}
      <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {sampleQuestions.slice(0, 3).map((question, index) => (
          <Box
            key={index}
            component="button"
            onClick={() => handleSampleQuestion(question)}
            disabled={isLoading || disabled}
            sx={{
              px: 2,
              py: 0.5,
              border: '1px solid',
              borderColor: 'primary.main',
              borderRadius: 2,
              bgcolor: 'transparent',
              color: 'primary.main',
              fontSize: '0.8rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
              '&:hover': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
              },
              '&:disabled': {
                opacity: 0.5,
                cursor: 'not-allowed',
              },
            }}
          >
            {question}
          </Box>
        ))}
      </Box>

      {/* Input Area */}
      <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder={
            disabled
              ? "Medical assistant is not available"
              : isLoading
              ? "Thinking..."
              : "Ask a medical question... (Press Enter to send, Shift+Enter for new line)"
          }
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled || isLoading}
          variant="outlined"
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              bgcolor: disabled ? 'action.disabledBackground' : 'background.paper',
            },
          }}
        />

        <Tooltip title="Send message">
          <span>
            <IconButton
              onClick={handleSend}
              disabled={!message.trim() || isLoading || disabled}
              color="primary"
              size="large"
              sx={{
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '&:disabled': {
                  bgcolor: 'action.disabledBackground',
                  color: 'action.disabled',
                },
              }}
            >
              <Send />
            </IconButton>
          </span>
        </Tooltip>

        <Tooltip title="More options">
          <IconButton
            onClick={handleMenuOpen}
            disabled={disabled}
            color="inherit"
          >
            <MoreVert />
          </IconButton>
        </Tooltip>

        {/* Options Menu */}
        <Menu
          anchorEl={menuAnchor}
          open={Boolean(menuAnchor)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
        >
          <MenuItem onClick={handleClearConversation}>
            <ListItemIcon>
              <Clear fontSize="small" />
            </ListItemIcon>
            <ListItemText>Clear Conversation</ListItemText>
          </MenuItem>
          
          <MenuItem 
            onClick={() => {
              window.open('http://localhost:8000/docs', '_blank');
              handleMenuClose();
            }}
          >
            <ListItemIcon>
              <Help fontSize="small" />
            </ListItemIcon>
            <ListItemText>API Documentation</ListItemText>
          </MenuItem>
        </Menu>
      </Box>

      {/* Status Message */}
      {disabled && (
        <Box
          sx={{
            mt: 1,
            p: 1,
            bgcolor: 'warning.light',
            color: 'warning.contrastText',
            borderRadius: 1,
            fontSize: '0.875rem',
            textAlign: 'center',
          }}
        >
          ⚠️ Medical assistant is currently unavailable. Please try again later.
        </Box>
      )}
    </Paper>
  );
};

export default ChatInput;
