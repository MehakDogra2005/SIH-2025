const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Store for connected clients
const clients = new Set();

// Server-Sent Events endpoint
app.get('/events', (req, res) => {
    // Set headers for SSE
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control'
    });

    // Add client to the set
    clients.add(res);

    // Send initial connection message
    res.write(`data: ${JSON.stringify({
        type: 'connection',
        message: 'Connected to drill notification system',
        timestamp: new Date().toISOString()
    })}\n\n`);

    // Handle client disconnect
    req.on('close', () => {
        clients.delete(res);
    });
});

// API endpoint to send notifications
app.post('/api/notify', (req, res) => {
    const { title, message, type = 'drill', participants = [] } = req.body;
    
    const notification = {
        id: Date.now().toString(),
        title,
        message,
        type,
        participants,
        timestamp: new Date().toISOString()
    };

    // Send to all connected clients
    const messageData = `data: ${JSON.stringify(notification)}\n\n`;
    
    clients.forEach(client => {
        try {
            client.write(messageData);
        } catch (error) {
            // Remove dead connections
            clients.delete(client);
        }
    });

    res.json({ success: true, notification });
});

// API endpoint to schedule a drill
app.post('/api/schedule-drill', (req, res) => {
    const drillData = {
        id: Date.now().toString(),
        ...req.body,
        createdAt: new Date().toISOString(),
        status: 'scheduled'
    };

    // Broadcast drill notification to all clients
    const notification = {
        id: Date.now().toString(),
        title: `New Drill Scheduled: ${drillData.title}`,
        message: `A ${drillData.type} drill has been scheduled for ${drillData.date} at ${drillData.time}`,
        type: 'drill_scheduled',
        drillId: drillData.id,
        participants: drillData.participants,
        timestamp: new Date().toISOString()
    };

    const messageData = `data: ${JSON.stringify(notification)}\n\n`;
    
    clients.forEach(client => {
        try {
            client.write(messageData);
        } catch (error) {
            clients.delete(client);
        }
    });

    res.json({ success: true, drill: drillData });
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        connectedClients: clients.size,
        timestamp: new Date().toISOString()
    });
});

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`🚨 Drill Notification System running on http://localhost:${PORT}`);
    console.log(`📡 Server-Sent Events available at http://localhost:${PORT}/events`);
    console.log(`🔔 Connected clients: ${clients.size}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('Shutting down server...');
    clients.forEach(client => {
        client.end();
    });
    process.exit(0);
});
