// QUANTUMNEX SECURITY MANAGER
// Industry Standards: OWASP Security Headers, Helmet.js, bcrypt.js, JWT tokens
// Validated Sources:
// - OWASP Security Headers (Web security standards)
// - Helmet.js (Express.js security middleware)
// - bcrypt.js (Password hashing)
// - JWT tokens (RFC 7519)

const helmet = require('helmet');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');
const crypto = require('crypto');

class QuantumNexSecurityManager {
    constructor() {
        this.encryptionRounds = 12;
        this.jwtSecret = process.env.JWT_SECRET || this.generateSecureSecret();
        this.securityHeaders = this.setupSecurityHeaders();
        this.rateLimiters = new Map();
        this.setupDefaultRateLimits();
    }

    setupSecurityHeaders() {
        return helmet({
            contentSecurityPolicy: {
                directives: {
                    defaultSrc: ["'self'"],
                    scriptSrc: ["'self'", "'unsafe-inline'"],
                    styleSrc: ["'self'", "'unsafe-inline'"],
                    imgSrc: ["'self'", "data:", "https:"],
                    connectSrc: ["'self'", "https://api.quantumnex.com"],
                    fontSrc: ["'self'", "https:"],
                    objectSrc: ["'none'"],
                    mediaSrc: ["'self'"],
                    frameSrc: ["'none'"]
                }
            },
            hsts: {
                maxAge: 31536000,
                includeSubDomains: true,
                preload: true
            },
            frameguard: { action: 'deny' },
            noSniff: true,
            xssFilter: true,
            referrerPolicy: { policy: 'strict-origin-when-cross-origin' }
        });
    }

    setupDefaultRateLimits() {
        // API rate limiting
        this.rateLimiters.set('api', rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutes
            max: 100, // Limit each IP to 100 requests per windowMs
            message: 'Too many API requests, please try again later.'
        }));

        // Authentication rate limiting
        this.rateLimiters.set('auth', rateLimit({
            windowMs: 60 * 60 * 1000, // 1 hour
            max: 5, // Limit each IP to 5 login attempts per hour
            message: 'Too many authentication attempts, please try again later.'
        }));

        // Trading rate limiting
        this.rateLimiters.set('trading', rateLimit({
            windowMs: 1 * 60 * 1000, // 1 minute
            max: 10, // Limit each IP to 10 trading requests per minute
            message: 'Too many trading requests, please slow down.'
        }));
    }

    generateSecureSecret() {
        return crypto.randomBytes(64).toString('hex');
    }

    // Password Security
    async hashPassword(password) {
        if (password.length < 8) {
            throw new Error('Password must be at least 8 characters long');
        }

        const salt = await bcrypt.genSalt(this.encryptionRounds);
        return await bcrypt.hash(password, salt);
    }

    async verifyPassword(password, hashedPassword) {
        return await bcrypt.compare(password, hashedPassword);
    }

    // JWT Token Management
    generateToken(payload, expiresIn = '24h') {
        return jwt.sign(payload, this.jwtSecret, { expiresIn });
    }

    verifyToken(token) {
        try {
            return jwt.verify(token, this.jwtSecret);
        } catch (error) {
            throw new Error('Invalid or expired token');
        }
    }

    decodeToken(token) {
        return jwt.decode(token);
    }

    // Input Validation
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    validatePasswordStrength(password) {
        const checks = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        const score = Object.values(checks).filter(Boolean).length;
        return {
            isValid: score >= 4,
            score,
            checks
        };
    }

    sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        
        // Remove potentially dangerous characters
        return input
            .replace(/[<>]/g, '')
            .replace(/javascript/gi, '')
            .replace(/on\w+=/gi, '')
            .trim();
    }

    // CSRF Protection
    generateCSRFToken() {
        return crypto.randomBytes(32).toString('hex');
    }

    verifyCSRFToken(token, sessionToken) {
        return token && sessionToken && token === sessionToken;
    }

    // Security Headers Middleware
    getSecurityHeaders() {
        return (req, res, next) => {
            // Additional security headers
            res.setHeader('X-Content-Type-Options', 'nosniff');
            res.setHeader('X-Frame-Options', 'DENY');
            res.setHeader('X-XSS-Protection', '1; mode=block');
            res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
            res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
            
            next();
        };
    }

    // Rate Limiting Middleware
    getRateLimiter(type = 'api') {
        return this.rateLimiters.get(type) || this.rateLimiters.get('api');
    }

    // Security Audit Logging
    logSecurityEvent(eventType, details) {
        const securityEvent = {
            id: crypto.randomBytes(16).toString('hex'),
            type: eventType,
            timestamp: new Date(),
            ip: details.ip,
            userAgent: details.userAgent,
            userId: details.userId,
            severity: details.severity || 'medium',
            details: details
        };

        console.log('í´’ SECURITY EVENT:', securityEvent);
        
        // In production, this would write to a secure audit log
        return securityEvent;
    }

    // API Key Management
    generateAPIKey() {
        const key = crypto.randomBytes(32).toString('hex');
        const secret = crypto.randomBytes(64).toString('hex');
        const hashedSecret = crypto.createHash('sha256').update(secret).digest('hex');

        return {
            key,
            secret, // Only returned once
            hashedSecret,
            createdAt: new Date()
        };
    }

    verifyAPIKey(apiKey, secret, hashedSecret) {
        const computedHash = crypto.createHash('sha256').update(secret).digest('hex');
        return computedHash === hashedSecret;
    }

    // Encryption Utilities
    encryptData(data, key = this.jwtSecret) {
        const algorithm = 'aes-256-gcm';
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipher(algorithm, key);

        let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
        encrypted += cipher.final('hex');

        const authTag = cipher.getAuthTag();

        return {
            iv: iv.toString('hex'),
            data: encrypted,
            authTag: authTag.toString('hex')
        };
    }

    decryptData(encryptedData, key = this.jwtSecret) {
        const algorithm = 'aes-256-gcm';
        const decipher = crypto.createDecipher(algorithm, key);

        decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));

        let decrypted = decipher.update(encryptedData.data, 'hex', 'utf8');
        decrypted += decipher.final('utf8');

        return JSON.parse(decrypted);
    }

    // Security Health Check
    performSecurityAudit() {
        const auditResults = {
            timestamp: new Date(),
            checks: {
                jwtSecret: this.jwtSecret !== 'quantumnex-default-secret',
                rateLimiting: this.rateLimiters.size > 0,
                headers: this.securityHeaders !== null,
                encryption: this.encryptionRounds >= 12
            },
            recommendations: []
        };

        if (auditResults.checks.jwtSecret === false) {
            auditResults.recommendations.push('Change default JWT secret in production');
        }

        if (auditResults.checks.encryptionRounds === false) {
            auditResults.recommendations.push('Increase encryption rounds for better security');
        }

        auditResults.score = Object.values(auditResults.checks).filter(Boolean).length / 
                            Object.keys(auditResults.checks).length * 100;

        return auditResults;
    }

    // Session Security
    generateSessionId() {
        return crypto.randomBytes(32).toString('hex');
    }

    validateSession(session, maxAge = 24 * 60 * 60 * 1000) { // 24 hours
        if (!session || !session.createdAt) {
            return false;
        }

        const sessionAge = Date.now() - new Date(session.createdAt).getTime();
        return sessionAge <= maxAge;
    }
}

module.exports = QuantumNexSecurityManager;
