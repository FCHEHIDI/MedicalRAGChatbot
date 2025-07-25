/**
 * MedicalDisclaimer Component
 * 
 * PURPOSE:
 * Displays critical medical safety warnings with every AI response.
 * Think of it as a "medical safety label" that reminds users that
 * AI is not a replacement for professional medical advice.
 * 
 * FUNCTIONALITY:
 * - Shows prominent warning alert for every AI medical response
 * - Uses warning color scheme (yellow/orange) for visibility
 * - Displays customizable disclaimer text from backend
 * - Ensures legal and ethical compliance
 * - Cannot be dismissed or hidden by users
 * 
 * MEDICAL CONTEXT:
 * Absolutely critical for medical applications. Protects both
 * users and the application by clearly stating AI limitations.
 * Required for legal compliance and ethical medical AI deployment.
 * 
 * LEGAL IMPORTANCE:
 * - Prevents medical liability issues
 * - Encourages professional medical consultation
 * - Clarifies AI assistant role vs. doctor role
 * - Required for responsible AI deployment
 * 
 * @component
 * @param {MedicalDisclaimerProps} props - Disclaimer text content
 * @returns {JSX.Element} Prominent medical safety warning
 */

import React from 'react';
import { Alert, AlertTitle, Box } from '@mui/material';
import { Warning } from '@mui/icons-material';
import { MedicalDisclaimerProps } from '../types';

const MedicalDisclaimer: React.FC<MedicalDisclaimerProps> = ({ disclaimer }) => {
  return (
    <Alert
      severity="warning"
      icon={<Warning />}
      sx={{
        mt: 1,
        bgcolor: 'warning.light',
        color: 'warning.contrastText',
        '& .MuiAlert-icon': {
          color: 'warning.main',
        },
      }}
    >
      <AlertTitle sx={{ fontSize: '0.875rem', fontWeight: 600 }}>
        Medical Disclaimer
      </AlertTitle>
      <Box sx={{ fontSize: '0.8rem', lineHeight: 1.4 }}>
        {disclaimer}
      </Box>
    </Alert>
  );
};

export default MedicalDisclaimer;
