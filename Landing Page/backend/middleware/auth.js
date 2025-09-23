const jwt = require('jsonwebtoken');
const User = require('../models/User');

const auth = async (req, res, next) => {
    try {
        const token = req.header('Authorization')?.replace('Bearer ', '');

        if (!token) {
            return res.status(401).json({ message: 'Access denied. No token provided.' });
        }

        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        console.log('🔑 Decoded token:', decoded); // Debug log

        // Direct database se user check karo
        const user = await User.findById(decoded.userId);

        if (!user) {
            return res.status(401).json({ message: 'Token is not valid - User not found' });
        }

        req.user = user; // Pure user object attach karo
        next();
    } catch (error) {
        console.error('Auth middleware error:', error);
        res.status(401).json({ message: 'Token is not valid' });
    }
};

module.exports = auth;