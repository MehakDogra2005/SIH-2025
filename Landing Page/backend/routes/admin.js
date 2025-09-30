const express = require('express');
const User = require('../models/User');
const auth = require('../middleware/auth');
const router = express.Router();

// Get all admin users (teachers) with optional floor and department filters
router.get('/teachers', auth, async (req, res) => {
    try {
        const { floor, department } = req.query;
        const query = { userType: 'admin' };

        // Add optional filters
        if (floor !== undefined) {
            query.floor = parseInt(floor);
        }
        if (department) {
            query.department = department;
        }

        const teachers = await User.find(query)
            .select('firstName lastName phoneNumber department floor email createdAt')
            .sort({ floor: 1, department: 1, firstName: 1 });

        // Convert to plain objects and add formatted dates
        const formattedTeachers = teachers.map(t => ({
            ...t.toObject(),
            createdAt: t.createdAt.toISOString()
        }));

        // Group teachers by floor
        const teachersByFloor = formattedTeachers.reduce((acc, teacher) => {
            const floorNum = teacher.floor;
            if (!acc[floorNum]) {
                acc[floorNum] = [];
            }
            acc[floorNum].push(teacher);
            return acc;
        }, {});

        res.json(teachersByFloor);
    } catch (error) {
        res.status(500).json({ message: 'Server error', error: error.message });
    }
});

// Get unique departments
router.get('/departments', auth, async (req, res) => {
    try {
        const departments = await User.distinct('department', {
            userType: 'admin',
            department: { $exists: true, $ne: '' }
        });
        res.json(departments);
    } catch (error) {
        res.status(500).json({ message: 'Server error', error: error.message });
    }
});

module.exports = router;