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
  Paper,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

const CentralizedAgentCore = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [accessMode, setAccessMode] = useState('backend');

  const sampleQueries = [
    "What is the banking performance in the East region?",
    "Analyze West region banking metrics",
    "Compare East vs West region ROA and assets",
    "Which region has better loan quality?",
    "Show me top banks in each region"
  ];

  const handleSubmit = async (queryText = null) => {
    const query = queryText || prompt;
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResponse('');

    try {
      const endpoint = accessMode === 'gateway' 
        ? process.env.REACT_APP_GATEWAY_URL || 'GATEWAY_URL_NOT_SET'
        : 'http://localhost:3001/api/chat-centralized';
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: query }),
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
      setError(`Network error: ${err.message}`);
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
          Centralized Multi-Account AgentCore
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
          Hub-and-spoke architecture: Central agent orchestrates queries across East and West regional banking accounts
        </Typography>
      </Paper>

      <Card sx={{ mb: 3, boxShadow: '0 4px 16px rgba(0,0,0,0.08)' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#A020F0' }}>
              🤖 Query Multi-Region Orchestrator
            </Typography>
            <ToggleButtonGroup
              value={accessMode}
              exclusive
              onChange={(e, newMode) => newMode && setAccessMode(newMode)}
              size="small"
            >
              <ToggleButton value="backend" sx={{ textTransform: 'none' }}>
                Backend Proxy
              </ToggleButton>
              <ToggleButton value="gateway" sx={{ textTransform: 'none' }}>
                Gateway (Serverless)
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>
          
          <Box sx={{ mb: 2, p: 2, backgroundColor: '#e3f2fd', borderRadius: 2, border: '1px solid #2196f3' }}>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1976d2' }}>
              🏗️ Architecture: Hub-and-Spoke (3 AWS Accounts)
            </Typography>
            <Typography variant="body2" sx={{ fontSize: '0.875rem', color: '#555' }}>
              • <strong>Central Account (164543933824)</strong>: Orchestrator agent (you are here)<br/>
              • <strong>East Region (891377397197)</strong>: Regional banking data + agent<br/>
              • <strong>West Region (058264155998)</strong>: Regional banking data + agent<br/>
              • <strong>Cross-Account Access</strong>: IAM AssumeRole for secure data access
            </Typography>
          </Box>
          
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
              placeholder="Ask about East region, West region, or compare both regions..."
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
