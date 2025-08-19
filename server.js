const fetchMcpServer = require('./fetch-mcp-server.js');
const tools = require('./tools.js');

const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

app.post('/api/process', async (req, res) => {
  try {
    const result = await fetchMcpServer.someFunction(req.body); // Replace with actual function call
    res.json({ result });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'An error occurred' });
  }
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
