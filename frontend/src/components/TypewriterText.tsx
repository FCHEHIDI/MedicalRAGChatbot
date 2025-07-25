/**
 * TypewriterText Component
 * 
 * PURPOSE:
 * Creates a natural typewriter effect for AI responses, making the bot
 * appear more conversational and human-like. This enhances user experience
 * by showing progressive text reveal instead of instant responses.
 * 
 * FUNCTIONALITY:
 * - Animates text character by character
 * - Configurable typing speed
 * - Supports markdown rendering during typing
 * - Calls completion callback when done
 * 
 * @component
 * @param {string} text - Text to animate
 * @param {number} speed - Typing speed in milliseconds
 * @param {function} onComplete - Callback when typing is complete
 */

import React, { useState, useEffect } from 'react';
import { Typography } from '@mui/material';
import ReactMarkdown from 'react-markdown';

interface TypewriterTextProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
}

const TypewriterText: React.FC<TypewriterTextProps> = ({ 
  text, 
  speed = 30, 
  onComplete 
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timeout);
    } else if (currentIndex === text.length && onComplete) {
      onComplete();
    }
  }, [currentIndex, text, speed, onComplete]);

  // Reset when text changes
  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
  }, [text]);

  return (
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
          <Typography component="ul" sx={{ pl: 2, mb: 1 }}>
            {children}
          </Typography>
        ),
        ol: ({ children }) => (
          <Typography component="ol" sx={{ pl: 2, mb: 1 }}>
            {children}
          </Typography>
        ),
        li: ({ children }) => (
          <Typography component="li" variant="body1" sx={{ mb: 0.5 }}>
            {children}
          </Typography>
        ),
      }}
    >
      {displayedText}
    </ReactMarkdown>
  );
};

export default TypewriterText;
