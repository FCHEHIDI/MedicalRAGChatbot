import React from 'react';
import { Box, Typography } from '@mui/material';
import { SmartToy } from '@mui/icons-material';

const TypingIndicator: React.FC = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'flex-start',
        mb: 2,
        gap: 1,
      }}
    >
      <SmartToy
        sx={{
          color: 'secondary.main',
          mt: 0.5,
        }}
      />
      <Box
        sx={{
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 2,
          p: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Medical assistant is thinking
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {[0, 1, 2].map((index) => (
            <Box
              key={index}
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                bgcolor: 'primary.main',
                animation: 'pulse 1.4s infinite',
                animationDelay: `${index * 0.2}s`,
                '@keyframes pulse': {
                  '0%, 80%, 100%': {
                    transform: 'scale(0.8)',
                    opacity: 0.5,
                  },
                  '40%': {
                    transform: 'scale(1)',
                    opacity: 1,
                  },
                },
              }}
            />
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default TypingIndicator;
