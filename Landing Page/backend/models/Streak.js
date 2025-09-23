const mongoose = require('mongoose');

const streakSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
    },
    currentStreak: {
        type: Number,
        default: 0
    },
    totalPoints: {
        type: Number,
        default: 0
    },
    lastCompletedDate: {
        type: Date,
        default: null
    },
    completedQuestions: [{
        date: {
            type: Date,
            required: true
        },
        points: {
            type: Number,
            required: true
        },
        questionId: {
            type: Number,
            required: true
        }
    }]
}, {
    timestamps: true
});

module.exports = mongoose.model('Streak', streakSchema);