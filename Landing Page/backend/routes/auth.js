const express = require('express');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const auth = require('../middleware/auth');
const router = express.Router();

// Signup API
router.post('/signup', async (req, res) => {
    try {
        const { firstName, lastName, email, password, institution, userType, phoneNumber, department, floor } = req.body;

        // Check if user already exists
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ message: 'User already exists with this email' });
        }

        // Validate admin fields if user type is admin
        if (userType === 'admin') {
            if (!phoneNumber || !department || floor === undefined) {
                return res.status(400).json({ message: 'Phone number, department, and floor are required for admin users' });
            }
            if (!/^\d{10}$/.test(phoneNumber)) {
                return res.status(400).json({ message: 'Invalid phone number format. Must be 10 digits.' });
            }
            if (floor < 0 || floor > 3) {
                return res.status(400).json({ message: 'Floor number must be between 0 and 3' });
            }
        }

        // Create new user
        const newUser = await User.create({
            firstName,
            lastName,
            email,
            password,
            institution,
            userType,
            ...(userType === 'admin' && {
                phoneNumber,
                department,
                floor
            })
        });

        // Generate JWT token
        const token = jwt.sign(
            { userId: newUser._id, email: newUser.email },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        res.status(201).json({
            message: 'User created successfully',
            token,
            user: {
                id: newUser._id,
                firstName: newUser.firstName,
                lastName: newUser.lastName,
                email: newUser.email,
                userType: newUser.userType,
                institution: newUser.institution,
                points: newUser.points,
                ...(newUser.userType === 'admin' && {
                    phoneNumber: newUser.phoneNumber,
                    department: newUser.department,
                    floor: newUser.floor
                })
            }
        });

    } catch (error) {
        res.status(500).json({ message: 'Server error', error: error.message });
    }
});

// Login API
// Login API - Return redirectUrl
router.post('/login', async (req, res) => {
    try {
        const { email, password, userType } = req.body;

        // Check if user exists
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(400).json({ message: 'Invalid email or password' });
        }

        // Check password
        const isPasswordValid = await user.correctPassword(password, user.password);
        if (!isPasswordValid) {
            return res.status(400).json({ message: 'Invalid email or password' });
        }

        // Check user type
        if (user.userType !== userType) {
            return res.status(400).json({ message: 'Invalid user type for this account' });
        }

        // Generate JWT token
        const token = jwt.sign(
            { userId: user._id, email: user.email },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        // ✅ Determine redirect URL based on user type
        let redirectUrl;
        if (user.userType === 'admin') {
            redirectUrl = 'http://localhost:5001/dashboard'; // Flask admin dashboard
        } else {
            redirectUrl = '/student/dashboard-student.html'; // Student dashboard
        }

        res.json({
            message: 'Login successful',
            token,
            user: {
                id: user._id,
                firstName: user.firstName,
                lastName: user.lastName,
                email: user.email,
                userType: user.userType,
                institution: user.institution,
                points: user.points
            },
            redirectUrl: redirectUrl // ✅ This is what the frontend will use
        });

    } catch (error) {
        res.status(500).json({ message: 'Server error', error: error.message });
    }
});

// Get current user API (requires authentication)
router.get('/current', auth, async (req, res) => {
    try {
        const user = await User.findById(req.user.id);  // 👈 direct DB se laa lo

        res.json({
            id: user._id,
            firstName: user.firstName,
            lastName: user.lastName,
            email: user.email,
            userType: user.userType,
            institution: user.institution,
            points: user.points,
            ...(user.userType === 'admin' && {
                phoneNumber: user.phoneNumber,
                department: user.department,
                floor: user.floor
            })
        });
    } catch (error) {
        res.status(500).json({ message: 'Server error', error: error.message });
    }
});


module.exports = router;