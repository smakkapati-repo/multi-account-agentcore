import React from 'react';
import { Typography, Box, Grid, Card, CardContent, Chip, Paper } from '@mui/material';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import AssessmentIcon from '@mui/icons-material/Assessment';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SecurityIcon from '@mui/icons-material/Security';
import CloudIcon from '@mui/icons-material/Cloud';

function Home() {
  const features = [
    {
      icon: <AnalyticsIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'Multi-Account Orchestration',
      description: 'Central orchestrator queries Corporate Banking and Treasury & Risk LOBs via MCP protocol across AWS accounts.',
      status: 'MCP-Enabled ✨'
    },
    {
      icon: <AssessmentIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'Credit Risk Assessment',
      description: 'Hybrid data: Real FDIC aggregate + synthetic customer loans. Real market rates + synthetic risk models (PD, LGD, Expected Loss).',
      status: 'AI-Powered'
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'Enterprise Architecture',
      description: 'Hub-and-spoke pattern with distributed LOB data ownership, cross-account IAM roles, and AgentCore Gateway.',
      status: 'Cloud-Native'
    }
  ];

  const stats = [
    { label: 'AWS Accounts', value: '3', color: '#00778f' },
    { label: 'LOB Agents', value: '2', color: '#00a897' },
    { label: 'MCP Tools', value: '7', color: '#02c59b' },
    { label: 'Fortune 500 Customers', value: '20', color: '#A020F0' }
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Paper 
        elevation={0} 
        sx={{ 
          background: 'linear-gradient(135deg, #A020F0 0%, #8B1A9B 50%, #6A1B9A 100%)',
          color: 'white',
          p: 3,
          borderRadius: 2,
          mb: 2
        }}
      >
        <Box textAlign="center" sx={{ maxWidth: '40%', mx: 'auto' }}>
          <AccountBalanceIcon sx={{ fontSize: 48, mb: 1 }} />
          <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 600, mb: 1 }}>
            LoanIQ
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
            Distributed Credit Risk Platform - Multi-Account Intelligence
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
            <Chip 
              icon={<CloudIcon />} 
              label="AWS Bedrock AgentCore" 
              sx={{ 
                backgroundColor: 'rgba(255,255,255,0.2)', 
                color: 'white',
                fontSize: '0.8rem'
              }} 
            />
            <Chip 
              label="Claude Sonnet 4.5" 
              sx={{ 
                backgroundColor: 'rgba(255,255,255,0.2)', 
                color: 'white',
                fontSize: '0.8rem'
              }} 
            />
          </Box>
        </Box>
      </Paper>

      {/* Stats Section */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ textAlign: 'center', p: 1.5, backgroundColor: stat.color, color: 'white' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
                {stat.value}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {stat.label}
              </Typography>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Features Section */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
        Key Features
      </Typography>
      
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                p: 2,
                transition: 'all 0.3s ease',
                '&:hover': { 
                  transform: 'translateY(-4px)', 
                  boxShadow: '0 8px 16px rgba(160, 32, 240, 0.15)'
                }
              }}
            >
              <CardContent sx={{ textAlign: 'center', p: 2, '&:last-child': { pb: 2 } }}>
                <Box sx={{ mb: 1 }}>
                  {React.cloneElement(feature.icon, { sx: { fontSize: 32, color: 'primary.main' } })}
                </Box>
                <Typography variant="subtitle1" component="h3" gutterBottom sx={{ fontWeight: 600 }}>
                  {feature.title}
                </Typography>
                <Typography color="text.secondary" sx={{ mb: 1, fontSize: '0.85rem', minHeight: 40 }}>
                  {feature.description}
                </Typography>
                <Chip 
                  label={feature.status}
                  size="small"
                  color={feature.status === 'Coming Soon' ? 'default' : 'primary'}
                  variant={feature.status === 'Coming Soon' ? 'outlined' : 'filled'}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Architecture Section */}
      <Box sx={{ mb: 3, p: 3, backgroundColor: '#e3f2fd', borderRadius: 2, border: '2px solid #2196f3' }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1976d2', mb: 2 }}>
          🏗️ Multi-Account Architecture
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, backgroundColor: 'white', borderRadius: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#A020F0' }}>
                Central Orchestrator
              </Typography>
              <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#555' }}>
                Coordinates credit risk queries across LOBs via MCP Client. No data storage - pure orchestration.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, backgroundColor: 'white', borderRadius: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#00a897' }}>
                Corporate Banking LOB
              </Typography>
              <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#555' }}>
                Customer loans & exposure data. MCP Server exposes tools for querying Fortune 500 relationships.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, backgroundColor: 'white', borderRadius: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#02c59b' }}>
                Treasury & Risk LOB
              </Typography>
              <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#555' }}>
                Risk models & treasury positions. MCP Server provides PD, LGD, Expected Loss calculations.
              </Typography>
            </Box>
          </Grid>
        </Grid>
        <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic', color: '#555' }}>
          • Cross-Account Access: Secure IAM AssumeRole + MCP protocol<br/>
          • Data Isolation: Each LOB maintains full control over sensitive data<br/>
          • No Data Duplication: Data stays in source accounts
        </Typography>
      </Box>

      {/* Technology Stack */}
      <Box sx={{ mt: 3, p: 2, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, textAlign: 'center', mb: 2 }}>
          Technology Stack
        </Typography>
        <Grid container spacing={1} justifyContent="center">
          {['AWS Bedrock AgentCore', 'MCP Protocol', 'Claude Sonnet 4.5', 'Strands Framework', 'AgentCore Gateway', 'Cross-Account IAM', 'FDIC API', 'FRED API', 'React'].map((tech) => (
            <Grid item key={tech}>
              <Chip 
                label={tech} 
                variant="outlined" 
                size="small"
                sx={{ 
                  borderColor: 'primary.main',
                  color: 'primary.main',
                  fontWeight: 500
                }}
              />
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
}

export default Home;