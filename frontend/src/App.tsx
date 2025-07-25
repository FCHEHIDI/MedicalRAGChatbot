import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Chip,
} from '@mui/material';
import {
  MedicalServices,
  Info,
  GitHub,
} from '@mui/icons-material';
import toast from 'react-hot-toast';
import ChatInterface from './components/ChatInterface';
import { chatService } from './services/chatService';
import { Message, ChatResponse } from './types';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>('');
  const [apiHealth, setApiHealth] = useState<'healthy' | 'unhealthy' | 'unknown'>('unknown');
  
  // Check API health on component mount
  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      const health = await chatService.getHealth();
      setApiHealth(health.status === 'healthy' ? 'healthy' : 'unhealthy');
    } catch (error) {
      setApiHealth('unhealthy');
      toast.error('Unable to connect to medical assistant API');
    }
  };

  const handleSendMessage = async (messageContent: string) => {
    if (isLoading || !messageContent.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageContent.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response: ChatResponse = await chatService.sendMessage({
        message: messageContent.trim(),
        conversation_id: conversationId || undefined,
        include_sources: true,
      });

      // Update conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: Message = {
        id: Date.now().toString() + '_assistant',
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        sources: response.sources,
        safetyDisclaimer: response.safety_disclaimer,
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error: any) {
      console.error('Error sending message:', error);
      
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Sorry, I encountered an error. Please try again.';
      
      toast.error(errorMessage);

      const errorResponse: Message = {
        id: Date.now().toString() + '_error',
        role: 'assistant',
        content: 'I apologize, but I encountered an error while processing your request. Please try again or contact support if the problem persists.',
        timestamp: new Date(),
        isError: true,
      };

      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearConversation = async () => {
    try {
      if (conversationId) {
        await chatService.clearConversation(conversationId);
      }
      setMessages([]);
      setConversationId('');
      toast.success('Conversation cleared');
    } catch (error) {
      toast.error('Failed to clear conversation');
    }
  };

  const getStatusColor = () => {
    switch (apiHealth) {
      case 'healthy': return 'success';
      case 'unhealthy': return 'error';
      default: return 'warning';
    }
  };

  const getStatusText = () => {
    switch (apiHealth) {
      case 'healthy': return 'Connected';
      case 'unhealthy': return 'Disconnected';
      default: return 'Checking...';
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* App Bar */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <MedicalServices sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Medical RAG Chatbot
          </Typography>
          
          <Chip
            icon={<Info />}
            label={getStatusText()}
            color={getStatusColor()}
            variant="outlined"
            sx={{ mr: 2, color: 'white', borderColor: 'rgba(255,255,255,0.5)' }}
          />
          
          <IconButton
            color="inherit"
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
          >
            <GitHub />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: 2, height: 'calc(100vh - 64px)' }}>
        <Paper
          elevation={2}
          sx={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* Welcome Header */}
          {messages.length === 0 && (
            <Box sx={{ p: 3, textAlign: 'center', bgcolor: 'primary.main', color: 'white' }}>
              <Typography variant="h4" gutterBottom>
                🩺 AI Medical Assistant
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Ask me any medical question and I'll provide evidence-based information with source citations.
              </Typography>
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: 1 }}>
                <Chip label="Evidence-Based" variant="outlined" sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }} />
                <Chip label="Source Citations" variant="outlined" sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }} />
                <Chip label="RAG Technology" variant="outlined" sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }} />
              </Box>
            </Box>
          )}

          {/* Chat Interface */}
          <ChatInterface
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onClearConversation={handleClearConversation}
            disabled={apiHealth !== 'healthy'}
          />
        </Paper>
      </Container>
    </Box>
  );
};

export default App;
