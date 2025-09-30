const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
    firstName: { type: String, required: true },
    lastName: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    phoneNumber: {
        type: String,
        required: function () {
            return this.userType === 'admin';
        },
        validate: {
            validator: function (v) {
                return /^\d{10}$/.test(v);
            },
            message: props => `${props.value} is not a valid phone number! Must be 10 digits.`
        }
    },
    institution: { type: String, required: true },
    userType: { type: String, enum: ['student', 'admin'], required: true },
    points: { type: Number, default: 0 },
    createdAt: { type: Date, default: Date.now },
    floor: {
        type: Number,
        required: function () {
            return this.userType === 'admin';
        },
        min: 0,
        max: 3
    },
    department: {
        type: String,
        required: function () {
            return this.userType === 'admin';
        }
    }
});

// Password encryption before saving
userSchema.pre('save', async function (next) {
    if (!this.isModified('password')) return next();
    this.password = await bcrypt.hash(this.password, 12);
    next();
});

// Password comparison method
userSchema.methods.correctPassword = async function (candidatePassword, userPassword) {
    return await bcrypt.compare(candidatePassword, userPassword);
};

module.exports = mongoose.model('User', userSchema);