const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const authRoutes = require('./routes/auth');
const streakRoutes = require('./routes/streakRoutes');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/streak', streakRoutes);

// ✅ FIXED MongoDB Connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/sih2025';

console.log('=====================================');
console.log('🔗 ATTEMPTING MONGODB CONNECTION...');
console.log('URI:', MONGODB_URI);
console.log('=====================================');

mongoose.connect(MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
    .then(() => {
        console.log('✅ MongoDB CONNECTED SUCCESSFULLY!');
        console.log('📊 Database Name:', mongoose.connection.db.databaseName);
        console.log('🏠 Host:', mongoose.connection.host);
        console.log('=====================================');
    })
    .catch(err => {
        console.log('❌ MONGODB CONNECTION FAILED!');
        console.log('Error:', err.message);
        console.log('=====================================');
        process.exit(1); // Exit if DB connection fails
    });

// Basic route to test if server is working
app.get('/api/test', (req, res) => {
    res.json({
        message: 'Server is running!',
        timestamp: new Date().toISOString(),
        database: mongoose.connection.db?.databaseName || 'Not connected'
    });
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`🚀 SERVER RUNNING ON PORT ${PORT}`);
    console.log(`📡 Test URL: http://localhost:${PORT}/api/test`);
    console.log('=====================================');
});