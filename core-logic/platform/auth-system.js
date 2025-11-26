// QUANTUMNEX AUTHENTICATION SYSTEM
// Industry Standards: NextAuth.js, Passport.js, OAuth2 standards
// Validated Sources:
// - NextAuth.js (Next.js authentication)
// - Passport.js (Node.js authentication middleware)
// - OAuth 2.0 RFC 6749
// - JWT RFC 7519

const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

class QuantumNexAuthSystem {
    constructor() {
        this.sessions = new Map();
        this.users = new Map();
        this.oauthProviders = new Map();
        this.jwtSecret = process.env.JWT_SECRET || 'quantumnex-default-secret';
        this.setupOAuthProviders();
    }

    setupOAuthProviders() {
        // Configure OAuth providers
        this.oauthProviders.set('google', {
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
            authUrl: 'https://accounts.google.com/o/oauth2/auth',
            tokenUrl: 'https://oauth2.googleapis.com/token',
            scope: 'email profile'
        });
        
        this.oauthProviders.set('github', {
            clientId: process.env.GITHUB_CLIENT_ID,
            clientSecret: process.env.GITHUB_CLIENT_SECRET,
            authUrl: 'https://github.com/login/oauth/authorize',
            tokenUrl: 'https://github.com/login/oauth/access_token',
            scope: 'user:email'
        });
    }

    async registerUser(email, password, userData = {}) {
        if (this.users.has(email)) {
            throw new Error('User already exists');
        }

        const hashedPassword = await bcrypt.hash(password, 12);
        const userId = uuidv4();
        
        const user = {
            id: userId,
            email,
            password: hashedPassword,
            ...userData,
            createdAt: new Date(),
            lastLogin: null,
            isActive: true,
            role: 'user'
        };

        this.users.set(email, user);
        return { userId, email };
    }

    async authenticateUser(email, password) {
        const user = this.users.get(email);
        if (!user || !user.isActive) {
            throw new Error('Invalid credentials');
        }

        const isValidPassword = await bcrypt.compare(password, user.password);
        if (!isValidPassword) {
            throw new Error('Invalid credentials');
        }

        user.lastLogin = new Date();
        return this.generateSession(user);
    }

    generateSession(user) {
        const sessionId = uuidv4();
        const token = jwt.sign(
            {
                userId: user.id,
                email: user.email,
                role: user.role,
                sessionId: sessionId
            },
            this.jwtSecret,
            { expiresIn: '24h' }
        );

        const session = {
            sessionId,
            userId: user.id,
            token,
            createdAt: new Date(),
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
            isActive: true
        };

        this.sessions.set(sessionId, session);
        return { token, sessionId, user: { id: user.id, email: user.email, role: user.role } };
    }

    verifyToken(token) {
        try {
            const decoded = jwt.verify(token, this.jwtSecret);
            const session = this.sessions.get(decoded.sessionId);
            
            if (!session || !session.isActive || session.expiresAt < new Date()) {
                throw new Error('Invalid session');
            }

            return decoded;
        } catch (error) {
            throw new Error('Invalid token');
        }
    }

    async oauthAuthenticate(provider, code, redirectUri) {
        const oauthConfig = this.oauthProviders.get(provider);
        if (!oauthConfig) {
            throw new Error('OAuth provider not configured');
        }

        // Simulate OAuth flow
        const userProfile = await this.simulateOAuthFlow(provider, code);
        
        // Find or create user
        let user = this.findUserByOAuthId(provider, userProfile.id);
        if (!user) {
            user = await this.createUserFromOAuthProfile(provider, userProfile);
        }

        return this.generateSession(user);
    }

    async simulateOAuthFlow(provider, code) {
        // Simulate OAuth token exchange and profile retrieval
        return {
            id: `oauth_${provider}_${code}`,
            email: `user@${provider}.com`,
            name: `${provider} User`,
            provider: provider
        };
    }

    findUserByOAuthId(provider, oauthId) {
        for (const user of this.users.values()) {
            if (user.oauthProvider === provider && user.oauthId === oauthId) {
                return user;
            }
        }
        return null;
    }

    async createUserFromOAuthProfile(provider, profile) {
        const userId = uuidv4();
        const user = {
            id: userId,
            email: profile.email,
            oauthProvider: provider,
            oauthId: profile.id,
            name: profile.name,
            createdAt: new Date(),
            lastLogin: new Date(),
            isActive: true,
            role: 'user'
        };

        this.users.set(profile.email, user);
        return user;
    }

    invalidateSession(sessionId) {
        const session = this.sessions.get(sessionId);
        if (session) {
            session.isActive = false;
            return true;
        }
        return false;
    }

    getUserSessions(userId) {
        const userSessions = [];
        for (const session of this.sessions.values()) {
            if (session.userId === userId && session.isActive) {
                userSessions.push(session);
            }
        }
        return userSessions;
    }

    updateUserRole(userId, newRole) {
        for (const user of this.users.values()) {
            if (user.id === userId) {
                user.role = newRole;
                return true;
            }
        }
        return false;
    }

    getSystemStats() {
        return {
            totalUsers: this.users.size,
            activeSessions: Array.from(this.sessions.values()).filter(s => s.isActive).length,
            oauthProviders: Array.from(this.oauthProviders.keys())
        };
    }
}

module.exports = QuantumNexAuthSystem;
