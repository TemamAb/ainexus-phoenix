/**
 * QUANTUMNEX ADMIN PANEL
 * Industry Standards: RBAC (Role-Based Access Control), CASL.js, Admin security patterns
 * Validated Sources:
 * - RBAC patterns (Role-Based Access Control)
 * - CASL.js (Authorization library)
 * - Admin security best practices
 */

const { Ability, AbilityBuilder } = require('@casl/ability');

class AdminPanel {
    constructor() {
        this.users = new Map();
        this.roles = new Map();
        this.auditLog = [];
        this.ability = this.defineAbilities();
        
        this.initializeDefaultRoles();
        console.log('âœ… Admin Panel initialized with RBAC patterns');
    }

    initializeDefaultRoles() {
        // Define default roles with permissions
        this.roles.set('super_admin', {
            name: 'Super Administrator',
            permissions: ['*'], // All permissions
            description: 'Full system access'
        });

        this.roles.set('admin', {
            name: 'Administrator',
            permissions: [
                'read', 'write', 'delete', 'manage_users',
                'view_analytics', 'system_config'
            ],
            description: 'System administration access'
        });

        this.roles.set('moderator', {
            name: 'Moderator',
            permissions: [
                'read', 'write', 'manage_users'
            ],
            description: 'User management access'
        });

        this.roles.set('viewer', {
            name: 'Viewer',
            permissions: ['read', 'view_analytics'],
            description: 'Read-only access'
        });
    }

    defineAbilities() {
        const { can, cannot, build } = new AbilityBuilder(Ability);

        // Super admin can do everything
        can('manage', 'all');

        // Admin permissions
        can(['read', 'write', 'delete'], ['User', 'Transaction', 'System']);
        can('manage_users', 'User');
        can('view_analytics', 'Analytics');
        can('system_config', 'System');

        // Moderator permissions
        can(['read', 'write'], 'User');
        can('manage_users', 'User');

        // Viewer permissions
        can('read', ['User', 'Transaction', 'Analytics']);
        can('view_analytics', 'Analytics');

        // Restrictions
        cannot('delete', 'User').because('User deletion requires super admin approval');
        cannot('system_config', 'System').because('System configuration requires admin role');

        return build();
    }

    async createUser(userData) {
        try {
            this.validateUserData(userData);
            
            const userId = this.generateUserId();
            const user = {
                id: userId,
                ...userData,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                isActive: true,
                loginAttempts: 0,
                lastLogin: null
            };

            this.users.set(userId, user);
            
            await this.auditAction('USER_CREATED', `User ${user.email} created`, userId);
            
            console.log(`âœ… User created: ${user.email} with role ${user.role}`);
            return user;
        } catch (error) {
            console.error('âŒ User creation failed:', error);
            throw error;
        }
    }

    validateUserData(userData) {
        const requiredFields = ['email', 'role', 'createdBy'];
        const missingFields = requiredFields.filter(field => !userData[field]);
        
        if (missingFields.length > 0) {
            throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
        }

        if (!this.isValidEmail(userData.email)) {
            throw new Error('Invalid email address');
        }

        if (!this.roles.has(userData.role)) {
            throw new Error(`Invalid role: ${userData.role}`);
        }

        return true;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    generateUserId() {
        return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async updateUser(userId, updates, updaterId) {
        try {
            const user = this.users.get(userId);
            if (!user) {
                throw new Error('User not found');
            }

            // Check if updater has permission
            if (!this.canManageUser(updaterId, userId)) {
                throw new Error('Insufficient permissions to update user');
            }

            // Validate role changes
            if (updates.role && updates.role !== user.role) {
                if (!this.canChangeRole(updaterId, updates.role)) {
                    throw new Error('Insufficient permissions to assign this role');
                }
            }

            const updatedUser = {
                ...user,
                ...updates,
                updatedAt: new Date().toISOString(),
                updatedBy: updaterId
            };

            this.users.set(userId, updatedUser);
            
            await this.auditAction('USER_UPDATED', `User ${user.email} updated`, updaterId, { userId, updates });
            
            console.log(`âœ… User updated: ${user.email}`);
            return updatedUser;
        } catch (error) {
            console.error('âŒ User update failed:', error);
            throw error;
        }
    }

    async deleteUser(userId, deleterId) {
        try {
            const user = this.users.get(userId);
            if (!user) {
                throw new Error('User not found');
            }

            // Check if deleter has permission
            if (!this.canDeleteUser(deleterId, userId)) {
                throw new Error('Insufficient permissions to delete user');
            }

            // Soft delete - mark as inactive
            user.isActive = false;
            user.deletedAt = new Date().toISOString();
            user.deletedBy = deleterId;

            this.users.set(userId, user);
            
            await this.auditAction('USER_DELETED', `User ${user.email} deleted`, deleterId, { userId });
            
            console.log(`âœ… User deleted: ${user.email}`);
            return user;
        } catch (error) {
            console.error('âŒ User deletion failed:', error);
            throw error;
        }
    }

    canManageUser(managerId, targetUserId) {
        const manager = this.users.get(managerId);
        const targetUser = this.users.get(targetUserId);
        
        if (!manager || !targetUser) return false;

        // Super admin can manage anyone
        if (manager.role === 'super_admin') return true;

        // Admin can manage non-admin users
        if (manager.role === 'admin' && targetUser.role !== 'super_admin') return true;

        // Users can only manage themselves for basic updates
        return managerId === targetUserId;
    }

    canChangeRole(managerId, newRole) {
        const manager = this.users.get(managerId);
        if (!manager) return false;

        // Only super admin can assign super_admin role
        if (newRole === 'super_admin' && manager.role !== 'super_admin') return false;

        // Admin can assign admin, moderator, viewer roles
        if (manager.role === 'admin' && ['admin', 'moderator', 'viewer'].includes(newRole)) return true;

        // Super admin can assign any role
        return manager.role === 'super_admin';
    }

    canDeleteUser(deleterId, targetUserId) {
        const deleter = this.users.get(deleterId);
        const targetUser = this.users.get(targetUserId);
        
        if (!deleter || !targetUser) return false;

        // Cannot delete yourself
        if (deleterId === targetUserId) return false;

        // Super admin can delete anyone
        if (deleter.role === 'super_admin') return true;

        // Admin can delete non-admin users
        return deleter.role === 'admin' && targetUser.role !== 'super_admin';
    }

    async systemOverride(user, command) {
        try {
            // Validate user has override permissions
            if (!this.canOverrideSystem(user.id)) {
                throw new Error('User does not have system override permissions');
            }

            // Validate command
            this.validateOverrideCommand(command);

            console.log(`í» ï¸ System override executed by ${user.email}: ${command.action}`);

            const result = await this.executeOverrideCommand(command);
            
            await this.auditAction(
                'SYSTEM_OVERRIDE', 
                `System override: ${command.action}`, 
                user.id, 
                { command, result }
            );

            return result;
        } catch (error) {
            console.error('âŒ System override failed:', error);
            await this.auditAction(
                'SYSTEM_OVERRIDE_FAILED',
                `System override failed: ${error.message}`,
                user.id,
                { command, error: error.message }
            );
            throw error;
        }
    }

    canOverrideSystem(userId) {
        const user = this.users.get(userId);
        return user && user.role === 'super_admin';
    }

    validateOverrideCommand(command) {
        if (!command || !command.action) {
            throw new Error('Invalid override command');
        }

        const allowedActions = [
            'emergency_stop',
            'force_withdrawal',
            'system_maintenance',
            'database_rollback',
            'config_override'
        ];

        if (!allowedActions.includes(command.action)) {
            throw new Error(`Invalid override action: ${command.action}`);
        }

        return true;
    }

    async executeOverrideCommand(command) {
        // Simulate command execution
        console.log(`âš¡ Executing override command: ${command.action}`);
        
        // Add artificial delay to simulate processing
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
            success: true,
            message: `Command ${command.action} executed successfully`,
            timestamp: new Date().toISOString()
        };
    }

    async auditAction(action, description, userId, metadata = {}) {
        const auditEntry = {
            id: this.generateAuditId(),
            action,
            description,
            userId,
            timestamp: new Date().toISOString(),
            ipAddress: metadata.ipAddress || '127.0.0.1',
            userAgent: metadata.userAgent || 'CLI',
            metadata
        };

        this.auditLog.push(auditEntry);
        
        // Keep only last 10,000 audit entries
        if (this.auditLog.length > 10000) {
            this.auditLog = this.auditLog.slice(-10000);
        }

        console.log(`í³ Audit: ${action} - ${description}`);
        return auditEntry;
    }

    generateAuditId() {
        return `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // User management methods
    getUser(userId) {
        return this.users.get(userId) || null;
    }

    getUserByEmail(email) {
        for (const [_, user] of this.users) {
            if (user.email === email && user.isActive) {
                return user;
            }
        }
        return null;
    }

    getAllUsers(includeInactive = false, limit = 100) {
        let users = Array.from(this.users.values());
        
        if (!includeInactive) {
            users = users.filter(user => user.isActive);
        }
        
        return users
            .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
            .slice(0, limit);
    }

    getUsersByRole(role, includeInactive = false) {
        let users = Array.from(this.users.values()).filter(user => user.role === role);
        
        if (!includeInactive) {
            users = users.filter(user => user.isActive);
        }
        
        return users;
    }

    // Role management methods
    createRole(roleData, creatorId) {
        try {
            this.validateRoleData(roleData);
            
            if (this.roles.has(roleData.id)) {
                throw new Error(`Role ${roleData.id} already exists`);
            }

            this.roles.set(roleData.id, {
                ...roleData,
                createdAt: new Date().toISOString(),
                createdBy: creatorId
            });

            console.log(`âœ… Role created: ${roleData.name}`);
            return roleData;
        } catch (error) {
            console.error('âŒ Role creation failed:', error);
            throw error;
        }
    }

    validateRoleData(roleData) {
        const requiredFields = ['id', 'name', 'permissions'];
        const missingFields = requiredFields.filter(field => !roleData[field]);
        
        if (missingFields.length > 0) {
            throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
        }

        if (!Array.isArray(roleData.permissions)) {
            throw new Error('Permissions must be an array');
        }

        return true;
    }

    getRole(roleId) {
        return this.roles.get(roleId) || null;
    }

    getAllRoles() {
        return Array.from(this.roles.values());
    }

    // Audit and reporting methods
    getAuditLog(filters = {}, limit = 100) {
        let entries = [...this.auditLog];

        if (filters.action) {
            entries = entries.filter(entry => entry.action === filters.action);
        }

        if (filters.userId) {
            entries = entries.filter(entry => entry.userId === filters.userId);
        }

        if (filters.startDate) {
            entries = entries.filter(entry => new Date(entry.timestamp) >= new Date(filters.startDate));
        }

        if (filters.endDate) {
            entries = entries.filter(entry => new Date(entry.timestamp) <= new Date(filters.endDate));
        }

        return entries.slice(-limit).reverse();
    }

    generateAdminReport(timeframe = '24h') {
        const now = new Date();
        let startTime;

        switch (timeframe) {
            case '1h':
                startTime = new Date(now.getTime() - 60 * 60 * 1000);
                break;
            case '24h':
                startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
                break;
            case '7d':
                startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            default:
                startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        }

        const recentAudit = this.getAuditLog({ startDate: startTime }, 1000);
        const userStats = this.calculateUserStats();

        const report = {
            timestamp: new Date().toISOString(),
            timeframe: timeframe,
            userStats: userStats,
            auditSummary: {
                totalActions: recentAudit.length,
                actionsByType: this.groupActionsByType(recentAudit),
                topUsers: this.getTopUsersByActivity(recentAudit, 5)
            },
            systemHealth: this.getSystemHealth(),
            recommendations: this.generateAdminRecommendations(userStats, recentAudit)
        };

        return report;
    }

    calculateUserStats() {
        const users = this.getAllUsers(true);
        
        return {
            totalUsers: users.length,
            activeUsers: users.filter(u => u.isActive).length,
            usersByRole: this.groupUsersByRole(users),
            recentSignups: users.filter(u => 
                new Date(u.createdAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
            ).length
        };
    }

    groupUsersByRole(users) {
        const grouped = {};
        users.forEach(user => {
            if (!grouped[user.role]) {
                grouped[user.role] = 0;
            }
            grouped[user.role]++;
        });
        return grouped;
    }

    groupActionsByType(auditEntries) {
        const grouped = {};
        auditEntries.forEach(entry => {
            if (!grouped[entry.action]) {
                grouped[entry.action] = 0;
            }
            grouped[entry.action]++;
        });
        return grouped;
    }

    getTopUsersByActivity(auditEntries, limit = 5) {
        const userActivity = {};
        
        auditEntries.forEach(entry => {
            if (!userActivity[entry.userId]) {
                userActivity[entry.userId] = 0;
            }
            userActivity[entry.userId]++;
        });

        return Object.entries(userActivity)
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([userId, count]) => ({ userId, count }));
    }

    getSystemHealth() {
        // Simplified system health check
        return {
            status: 'healthy',
            users: this.users.size,
            roles: this.roles.size,
            auditEntries: this.auditLog.length,
            lastHealthCheck: new Date().toISOString()
        };
    }

    generateAdminRecommendations(userStats, recentAudit) {
        const recommendations = [];

        if (userStats.activeUsers === 0) {
            recommendations.push({
                type: 'USER_MANAGEMENT',
                message: 'No active users in system',
                priority: 'high',
                action: 'Create initial admin user'
            });
        }

        const superAdminCount = userStats.usersByRole['super_admin'] || 0;
        if (superAdminCount === 0) {
            recommendations.push({
                type: 'SECURITY',
                message: 'No super admin users configured',
                priority: 'high',
                action: 'Assign super admin role to trusted user'
            });
        }

        const failedLogins = recentAudit.filter(entry => 
            entry.action === 'LOGIN_FAILED'
        ).length;

        if (failedLogins > 10) {
            recommendations.push({
                type: 'SECURITY',
                message: 'High number of failed login attempts',
                priority: 'medium',
                action: 'Review security logs and consider rate limiting'
            });
        }

        return recommendations;
    }

    // Utility methods
    can(user, action, subject) {
        return this.ability.can(action, subject);
    }

    getUserPermissions(userId) {
        const user = this.users.get(userId);
        if (!user) return [];
        
        const role = this.roles.get(user.role);
        return role ? role.permissions : [];
    }

    // Cleanup methods
    cleanupInactiveUsers(daysInactive = 90) {
        const cutoffDate = new Date(Date.now() - daysInactive * 24 * 60 * 60 * 1000);
        let cleanedCount = 0;

        for (const [userId, user] of this.users) {
            if (!user.isActive && new Date(user.updatedAt) < cutoffDate) {
                this.users.delete(userId);
                cleanedCount++;
            }
        }

        console.log(`í·¹ Cleaned up ${cleanedCount} inactive users`);
        return cleanedCount;
    }

    cleanupOldAuditLog(daysToKeep = 365) {
        const cutoffDate = new Date(Date.now() - daysToKeep * 24 * 60 * 60 * 1000);
        const initialCount = this.auditLog.length;
        
        this.auditLog = this.auditLog.filter(entry => 
            new Date(entry.timestamp) >= cutoffDate
        );

        const cleanedCount = initialCount - this.auditLog.length;
        console.log(`í·¹ Cleaned up ${cleanedCount} old audit entries`);
        return cleanedCount;
    }
}

module.exports = AdminPanel;
