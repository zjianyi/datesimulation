// Simple proxy server to handle CORS issues
const http = require('http');
const https = require('https');
const url = require('url');

const PORT = 3000;
const TARGET_URL = 'http://localhost:5001';

const server = http.createServer((req, res) => {
  console.log(`Received request: ${req.method} ${req.url}`);
  
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Get-Current-Only');
  
  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // Parse request URL
  const parsedUrl = url.parse(req.url);
  const targetUrl = `${TARGET_URL}${parsedUrl.path}`;
  
  console.log(`Proxying request to: ${targetUrl}`);
  
  // Create options for the proxied request
  const options = {
    method: req.method,
    headers: req.headers
  };
  
  // Create the proxied request
  const proxyReq = http.request(targetUrl, options, (proxyRes) => {
    // Set response headers
    Object.keys(proxyRes.headers).forEach(key => {
      res.setHeader(key, proxyRes.headers[key]);
    });
    
    // Set status code
    res.writeHead(proxyRes.statusCode);
    
    // Pipe response data
    proxyRes.pipe(res);
  });
  
  // Handle errors
  proxyReq.on('error', (error) => {
    console.error('Proxy error:', error);
    res.writeHead(500);
    res.end(`Proxy error: ${error.message}`);
  });
  
  // Pipe request body
  req.pipe(proxyReq);
});

server.listen(PORT, () => {
  console.log(`Proxy server running on http://localhost:${PORT}`);
  console.log(`Forwarding requests to ${TARGET_URL}`);
}); 