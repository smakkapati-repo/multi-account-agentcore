import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Chip,
  Paper
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

const CentralizedAgentCore = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const sampleQueries = [
    "Show me Technology loans from Corporate Banking",
    "What are the risk models for Healthcare industry?",
    "Compare Corporate Banking vs Treasury & Risk exposure",
    "Get capital ratios for Wells Fargo",
    "Calculate expected loss for $100M Healthcare loan"
  ];

  const handleSubmit = async (queryText = null) => {
    const query = queryText || prompt;
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResponse('');

    try {
      const gatewayUrl = process.env.REACT_APP_GATEWAY_URL;
      
      if (!gatewayUrl) {
        throw new Error('Gateway URL not configured. Set REACT_APP_GATEWAY_URL environment variable.');
      }
      
      const response = await fetch(gatewayUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.response) {
        const cleanText = data.response
          .replace(/\*\*([^*]+)\*\*/g, '$1')
          .replace(/\*([^*]+)\*/g, '$1')
          .replace(/^#+\s+/gm, '')
          .replace(/^[-*•]\s+/gm, '')
          .replace(/^\d+\.\s+/gm, '')
          .replace(/^[A-Z][^:]+:\s*/gm, '')
          .replace(/\n{3,}/g, '\n\n')
          .trim();
        
        setResponse(cleanText);
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Paper 
        elevation={0} 
        sx={{ 
          background: 'linear-gradient(135deg, #A020F0 0%, #8B1A9B 100%)',
          color: 'white',
          p: 2,
          borderRadius: 2,
          mb: 3,
          textAlign: 'center'
        }}
      >
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Multi-Account Credit Risk Orchestrator
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
          Hub-and-spoke architecture: Central orchestrator queries Corporate Banking and Treasury & Risk LOBs via MCP protocol
        </Typography>
      </Paper>

      <Card sx={{ mb: 3, boxShadow: '0 4px 16px rgba(0,0,0,0.08)' }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#A020F0', mb: 2 }}>
            🤖 Query Credit Risk Orchestrator
          </Typography>
          
          <Box sx={{ mb: 2, p: 2, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
              💡 Sample Queries:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {sampleQueries.map((query, index) => (
                <Chip
                  key={index}
                  label={query}
                  onClick={() => handleSubmit(query)}
                  variant="outlined"
                  size="small"
                  sx={{ 
                    cursor: 'pointer',
                    borderColor: '#A020F0',
                    color: '#A020F0',
                    '&:hover': { 
                      backgroundColor: '#A020F0',
                      color: 'white'
                    }
                  }}
                />
              ))}
            </Box>
          </Box>

          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask about Corporate Banking loans, Treasury & Risk models, or compare LOBs..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&:hover fieldset': { borderColor: '#A020F0' },
                  '&.Mui-focused fieldset': { borderColor: '#A020F0' }
                }
              }}
            />
            <Button
              variant="contained"
              onClick={() => handleSubmit()}
              disabled={loading || !prompt.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              sx={{ minWidth: '140px' }}
            >
              {loading ? 'Processing...' : 'Send'}
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {response && (
            <Card variant="outlined" sx={{ 
              background: 'linear-gradient(135deg, #f8f9ff, #ffffff)',
              border: '2px solid #A020F0'
            }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#A020F0' }}>
                  🎯 Agent Response:
                </Typography>
                <Box sx={{ 
                  lineHeight: 1.8,
                  color: '#333',
                  fontSize: '1rem',
                  whiteSpace: 'pre-wrap',
                  backgroundColor: 'white',
                  p: 3,
                  borderRadius: 1
                }}>
                  {response.split('\n\n').map((paragraph, index) => (
                    paragraph.trim() && (
                      <Typography 
                        key={index} 
                        component="p" 
                        sx={{ 
                          mb: 2,
                          textAlign: 'justify',
                          '&:last-child': { mb: 0 }
                        }}
                      >
                        {paragraph.trim()}
                      </Typography>
                    )
                  ))}
                </Box>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default CentralizedAgentCore;
