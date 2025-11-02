const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', service: 'Multi-Account POC Backend' });
});

// Invoke multi-account agent endpoint
app.post('/api/invoke-agent', async (req, res) => {
  try {
    const { prompt } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    console.log(`[Agent] Invoking with prompt: ${prompt}`);

    // Execute agentcore invoke command
    const agentDir = path.join(__dirname, '../agent');
    const escapedPrompt = prompt.replace(/"/g, '\\"').replace(/'/g, "'\"'\"'");
    const command = `cd ${agentDir} && agentcore invoke '{"prompt": "${escapedPrompt}"}'`;
    
    exec(command, { maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (error) {
        console.error(`[Agent] Error: ${error.message}`);
        return res.status(500).json({ 
          error: 'Agent invocation failed',
          details: error.message 
        });
      }

      if (stderr) {
        console.error(`[Agent] Stderr: ${stderr}`);
      }

      console.log(`[Agent] Response received`);
      
      res.json({ 
        success: true,
        response: stdout,
        prompt: prompt
      });
    });

  } catch (error) {
    console.error(`[Agent] Unexpected error: ${error.message}`);
    res.status(500).json({ 
      error: 'Internal server error',
      details: error.message 
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Multi-Account POC Backend running on port ${PORT}`);
  console.log(`📡 Agent API: http://localhost:${PORT}/api/invoke-agent`);
});

module.exports = app;