const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const Streak = require('../models/Streak');

// Get user streak data - SUPER SIMPLE VERSION
router.get('/user-streak', auth, async (req, res) => {
    try {
        console.log('🎯 /api/streak/user-streak CALLED!');
        console.log('User ID:', req.user._id);

        let streak = await Streak.findOne({ userId: req.user._id });

        if (!streak) {
            console.log('Creating NEW streak for user');
            streak = new Streak({
                userId: req.user._id,
                currentStreak: 0,
                totalPoints: 0,
                lastCompletedDate: null,
                completedQuestions: []
            });
            await streak.save();
            console.log('✅ New streak created');
        }

        console.log('📊 Sending streak data:', streak);
        res.json(streak);

    } catch (error) {
        console.error('❌ ERROR in /api/streak/user-streak:', error);
        res.status(500).json({
            success: false,
            message: 'Server error',
            error: error.message
        });
    }
});

// Update streak data - SUPER SIMPLE VERSION
router.post('/update-streak', auth, async (req, res) => {
    try {
        console.log('🎯 /api/streak/update-streak CALLED!');
        console.log('User ID:', req.user._id);
        console.log('Request Body:', req.body);

        let streak = await Streak.findOne({ userId: req.user._id });

        if (!streak) {
            streak = new Streak({
                userId: req.user._id,
                ...req.body
            });
        } else {
            Object.assign(streak, req.body);
        }

        const savedStreak = await streak.save();
        console.log('✅ Streak saved to database');

        res.json({
            success: true,
            message: 'Streak updated successfully',
            streak: savedStreak
        });

    } catch (error) {
        console.error('❌ ERROR in /api/streak/update-streak:', error);
        res.status(500).json({
            success: false,
            message: 'Server error',
            error: error.message
        });
    }
});

module.exports = router;