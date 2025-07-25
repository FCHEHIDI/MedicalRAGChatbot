/**
 * SourceCitations Component
 * 
 * PURPOSE:
 * Displays medical document sources that support the AI's response.
 * Think of it as a "bibliography" or "reference list" that shows
 * where the medical information came from, ensuring transparency.
 * 
 * FUNCTIONALITY:
 * - Shows collapsible list of medical sources
 * - Displays relevance scores for each source
 * - Provides expandable source content preview
 * - Color-codes sources by relevance score
 * - Allows users to verify AI medical claims
 * 
 * MEDICAL CONTEXT:
 * Critical for medical trustworthiness. Users can verify that
 * AI responses are based on legitimate medical sources, not
 * random internet content. Helps build confidence in AI guidance.
 * 
 * VISUAL STRUCTURE:
 * [📚 Sources (3)] [Expand/Collapse]
 *   ├── Source 1 [Score: 0.95] [High Relevance - Green]
 *   ├── Source 2 [Score: 0.82] [Medium Relevance - Yellow]  
 *   └── Source 3 [Score: 0.71] [Lower Relevance - Gray]
 * 
 * @component
 * @param {SourceCitationsProps} props - Medical sources data
 * @returns {JSX.Element} Expandable medical sources list
 */

import React from 'react';
import { Box, Typography, Chip, Collapse, Paper } from '@mui/material';
import { ExpandMore, ExpandLess, Source } from '@mui/icons-material';
import { SourceCitationsProps } from '../types';

const SourceCitations: React.FC<SourceCitationsProps> = ({ sources }) => {
  const [expanded, setExpanded] = React.useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  return (
    <Paper
      elevation={0}
      sx={{
        border: '1px solid',
        borderColor: 'primary.light',
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box
        onClick={handleToggle}
        sx={{
          p: 1.5,
          bgcolor: 'primary.light',
          color: 'primary.contrastText',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          '&:hover': {
            bgcolor: 'primary.main',
          },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Source fontSize="small" />
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            Medical Sources ({sources.length})
          </Typography>
        </Box>
        {expanded ? <ExpandLess /> : <ExpandMore />}
      </Box>

      {/* Sources List */}
      <Collapse in={expanded}>
        <Box sx={{ p: 1 }}>
          {sources.map((source, index) => (
            <Paper
              key={index}
              elevation={0}
              sx={{
                p: 2,
                mb: index < sources.length - 1 ? 1 : 0,
                bgcolor: 'grey.50',
                border: '1px solid',
                borderColor: 'grey.200',
                borderRadius: 1,
              }}
            >
              {/* Source Header */}
              <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 600,
                    color: 'primary.main',
                    flex: 1,
                    lineHeight: 1.3,
                  }}
                >
                  {source.title}
                </Typography>
                <Chip
                  label={`${Math.round(source.score * 100)}% match`}
                  size="small"
                  color={source.score > 0.8 ? 'success' : source.score > 0.6 ? 'warning' : 'default'}
                  sx={{ ml: 1, fontSize: '0.7rem', height: 20 }}
                />
              </Box>

              {/* Source Content */}
              <Typography
                variant="body2"
                sx={{
                  color: 'text.secondary',
                  lineHeight: 1.5,
                  fontSize: '0.875rem',
                }}
              >
                {source.content.length > 300
                  ? `${source.content.substring(0, 300)}...`
                  : source.content}
              </Typography>

              {/* Metadata */}
              {source.metadata && (
                <Box sx={{ mt: 1.5, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {source.metadata.specialty && (
                    <Chip
                      label={source.metadata.specialty}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.7rem', height: 20 }}
                    />
                  )}
                  {source.metadata.document_type && (
                    <Chip
                      label={source.metadata.document_type}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.7rem', height: 20 }}
                    />
                  )}
                  {source.metadata.authors && (
                    <Chip
                      label={`By: ${source.metadata.authors}`}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.7rem', height: 20 }}
                    />
                  )}
                </Box>
              )}
            </Paper>
          ))}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default SourceCitations;
