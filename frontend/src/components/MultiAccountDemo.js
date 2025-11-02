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
  Grid,
  Paper
} from '@mui/material';
import { Send as SendIcon, AccountBalance, CloudQueue } from '@mui/icons-material';

const MultiAccountDemo = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const formatAsReport = (text) => {
    // Skip formatting if it's a meta-response or too short
    if (text.includes('previous response') || text.includes('already provided') || text.length < 500) {
      return text;
    }
    
    const sentences = text.split(/(?<=[.!?])\s+/).filter(s => s.length > 20);
    
    if (sentences.length < 3) return text;
    
    let formatted = '## Executive Summary\n\n' + sentences[0] + '\n\n';
    
    // Group remaining sentences into logical sections
    const midPoint = Math.floor(sentences.length / 2);
    
    formatted += '## Risk Assessment\n\n';
    formatted += sentences.slice(1, midPoint).join(' ') + '\n\n';
    
    formatted += '## Strategic Considerations\n\n';
    formatted += sentences.slice(midPoint).join(' ') + '\n\n';
    
    return formatted;
  };

  const sampleQueries = [
    "Assess trade finance risk for Tesla Inc",
    "Compare financial health of Microsoft vs Amazon",
    "What are the trade risks for companies operating in China?",
    "Analyze Alphabet Inc's exposure to Vietnam markets",
    "Evaluate Apple Inc's risk profile for German trade operations"
  ];

  const handleSubmit = async (queryText = null) => {
    const query = queryText || prompt;
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResponse('');

    try {
      console.log('Making request to:', 'http://localhost:3001/api/invoke-agent');
      console.log('Query:', query);
      
      // Call the multi-account agent
      const response = await fetch('http://localhost:3001/api/invoke-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: query }),
      });
      
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        // Extract all text from the streaming response
        const responseText = data.response;
        let fullText = '';
        
        // Extract from all contentBlockDelta events
        const deltaMatches = responseText.match(/"contentBlockDelta":\s*\{"delta":\s*\{"text":\s*"([^"]*(?:\\.[^"]*)*)"/g);
        if (deltaMatches) {
          deltaMatches.forEach(match => {
            const textMatch = match.match(/"text":\s*"([^"]*(?:\\.[^"]*)*)"/); 
            if (textMatch) {
              fullText += textMatch[1]
                .replace(/\\n/g, '\n')
                .replace(/\\"/g, '"')
                .replace(/\\\\/g, '/')
                .replace(/\\t/g, '\t');
            }
          });
          
          // Decode HTML entities and clean formatting
          fullText = fullText
            .replace(/&#39;/g, "'")
            .replace(/&quot;/g, '"')
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/\s+/g, ' ')
            .trim();
          
          // Format as report only for substantial responses
          fullText = formatAsReport(fullText);
        }
        
        // If no delta matches, try to get the final message
        if (!fullText) {
          const messageMatch = responseText.match(/"message":[^}]+"text":\s*"([^"]+(?:\\.[^"]*)*)"/s);
          if (messageMatch) {
            fullText = messageMatch[1]
              .replace(/\\n/g, '\n')
              .replace(/\\"/g, '"')
              .replace(/\\\\/g, '/');
          }
        }
        
        setResponse(fullText || 'Agent response received but could not parse');
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (err) {
      console.error('Request failed:', err);
      setError(`Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        Multi-Account AgentCore Demo
      </Typography>

      {/* Architecture Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#f3e5f5' }}>
            <AccountBalance sx={{ fontSize: 40, color: '#7b1fa2', mb: 1 }} />
            <Typography variant="h6">Central Account</Typography>
            <Typography variant="body2" color="text.secondary">
              164543933824
            </Typography>
            <Typography variant="body2">
              AgentCore Orchestration
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#e8f5e8' }}>
            <CloudQueue sx={{ fontSize: 40, color: '#388e3c', mb: 1 }} />
            <Typography variant="h6">Child1 Financial KB</Typography>
            <Typography variant="body2" color="text.secondary">
              891377397197
            </Typography>
            <Typography variant="body2">
              SEC 10-K Filings
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#fff3e0' }}>
            <CloudQueue sx={{ fontSize: 40, color: '#f57c00', mb: 1 }} />
            <Typography variant="h6">Child2 Trade Risk KB</Typography>
            <Typography variant="body2" color="text.secondary">
              058264155998
            </Typography>
            <Typography variant="body2">
              Country Risk Data
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Query Interface */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Query Multi-Account Agent
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Sample Queries:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {sampleQueries.map((query, index) => (
                <Chip
                  key={index}
                  label={query}
                  onClick={() => handleSubmit(query)}
                  variant="outlined"
                  size="small"
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Box>

          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Enter your query..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
            />
            <Button
              variant="contained"
              onClick={() => handleSubmit()}
              disabled={loading || !prompt.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
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
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Agent Response:
                </Typography>
                <Box sx={{ 
                  '& h2': { 
                    color: '#1976d2', 
                    fontSize: '1.2rem', 
                    fontWeight: 600, 
                    mt: 2, 
                    mb: 1,
                    borderBottom: '2px solid #e3f2fd',
                    pb: 0.5
                  },
                  '& p': { 
                    textAlign: 'justify', 
                    lineHeight: 1.7, 
                    color: '#2c3e50',
                    mb: 1.5
                  }
                }}>
                  {response.split('\n').map((line, index) => {
                    if (line.startsWith('## ')) {
                      return <Typography key={index} variant="h6" component="h2">{line.replace('## ', '')}</Typography>;
                    } else if (line.trim()) {
                      return <Typography key={index} component="p">{line}</Typography>;
                    }
                    return <br key={index} />;
                  })}
                </Box>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>

      {/* Status Information */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Chip label="AgentCore" color="success" />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Deployed & Active
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Chip label="Child1 KB" color="success" />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  5 Companies
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Chip label="Child2 KB" color="success" />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  5 Countries
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Chip label="Cross-Account" color="success" />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  AssumeRole Active
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MultiAccountDemo;