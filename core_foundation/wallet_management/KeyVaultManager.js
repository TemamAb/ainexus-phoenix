/**
 * Advanced Cryptographic Key Vault Management System
 * Secure storage, rotation, and management of cryptographic keys
 */

const crypto = require('crypto');
const { EventEmitter } = require('events');
const { subtle } = require('crypto').webcrypto;

class KeyVaultManager extends EventEmitter {
    constructor(vaultName = 'default') {
        super();
        this.vaultName = vaultName;
        this.keys = new Map();
        this.keyVersions = new Map();
        this.accessPolicies = new Map();
        this.auditLog = [];
        this.encryptionKey = this.generateEncryptionKey();
        
        this.initializeSecurityProtocols();
    }

    initializeSecurityProtocols() {
        this.securityConfig = {
            keyRotation: {
                enabled: true,
                interval: 30 * 24 * 60 * 60 * 1000, // 30 days
                gracePeriod: 7 * 24 * 60 * 60 * 1000 // 7 days
            },
            encryption: {
                algorithm: 'aes-256-gcm',
                keyLength: 32
            },
            accessControl: {
                maxAttempts: 5,
                lockoutDuration: 15 * 60 * 1000 // 15 minutes
            },
            backup: {
                enabled: true,
                interval: 24 * 60 * 60 * 1000 // 24 hours
            }
        };

        this.failedAttempts = new Map();
        this.lockedKeys = new Set();
    }

    // Key Generation Methods
    async generateKey(keyId, keyType = 'aes', keySize = 256, metadata = {}) {
        console.log(`Generating ${keyType} key: ${keyId}`);

        let keyData;
        let publicKey = null;

        switch (keyType.toLowerCase()) {
            case 'aes':
                keyData = await this.generateAESKey(keySize);
                break;
            case 'rsa':
                const rsaKeys = await this.generateRSAKey(keySize);
                keyData = rsaKeys.privateKey;
                publicKey = rsaKeys.publicKey;
                break;
            case 'ec':
                const ecKeys = await this.generateECKey();
                keyData = ecKeys.privateKey;
                publicKey = ecKeys.publicKey;
                break;
            case 'hmac':
                keyData = this.generateHMACKey(keySize);
                break;
            default:
                throw new Error(`Unsupported key type: ${keyType}`);
        }

        const keyRecord = {
            keyId,
            keyType,
            keySize,
            keyData,
            publicKey,
            version: 1,
            createdAt: new Date(),
            lastUsed: null,
            expiresAt: new Date(Date.now() + this.securityConfig.keyRotation.interval),
            metadata,
            isActive: true,
            usageCount: 0
        };

        this.keys.set(keyId, keyRecord);
        
        // Initialize version history
        this.keyVersions.set(keyId, [this.serializeKeyRecord(keyRecord)]);

        this.audit('KEY_GENERATED', { keyId, keyType, keySize });

        this.emit('keyGenerated', {
            keyId,
            keyType,
            timestamp: new Date()
        });

        return keyRecord;
    }

    async generateAESKey(keySize = 256) {
        const keyBytes = keySize / 8;
        const key = crypto.randomBytes(keyBytes);
        return this.encryptKeyData(key.toString('base64'));
    }

    async generateRSAKey(keySize = 2048) {
        // In a real implementation, this would use proper Web Crypto API
        // This is a simplified version for demonstration
        const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
            modulusLength: keySize,
            publicKeyEncoding: {
                type: 'spki',
                format: 'pem'
            },
            privateKeyEncoding: {
                type: 'pkcs8',
                format: 'pem'
            }
        });

        return {
            publicKey: this.encryptKeyData(publicKey),
            privateKey: this.encryptKeyData(privateKey)
        };
    }

    async generateECKey() {
        // Simplified EC key generation
        const { publicKey, privateKey } = crypto.generateKeyPairSync('ec', {
            namedCurve: 'P-256',
            publicKeyEncoding: {
                type: 'spki',
                format: 'pem'
            },
            privateKeyEncoding: {
                type: 'pkcs8',
                format: 'pem'
            }
        });

        return {
            publicKey: this.encryptKeyData(publicKey),
            privateKey: this.encryptKeyData(privateKey)
        };
    }

    generateHMACKey(keySize = 256) {
        const keyBytes = keySize / 8;
        const key = crypto.randomBytes(keyBytes);
        return this.encryptKeyData(key.toString('base64'));
    }

    // Key Management Methods
    async rotateKey(keyId, newKeySize = null) {
        const existingKey = this.keys.get(keyId);
        if (!existingKey) {
            throw new Error(`Key not found: ${keyId}`);
        }

        console.log(`Rotating key: ${keyId}`);

        // Generate new key
        const newKey = await this.generateKey(
            keyId,
            existingKey.keyType,
            newKeySize || existingKey.keySize,
            existingKey.metadata
        );

        // Update version
        newKey.version = existingKey.version + 1;
        
        // Archive old key
        existingKey.isActive = false;
        existingKey.rotatedAt = new Date();

        // Update key store
        this.keys.set(keyId, newKey);

        // Add to version history
        this.keyVersions.get(keyId).push(this.serializeKeyRecord(newKey));

        this.audit('KEY_ROTATED', { 
            keyId, 
            oldVersion: existingKey.version,
            newVersion: newKey.version 
        });

        this.emit('keyRotated', {
            keyId,
            oldVersion: existingKey.version,
            newVersion: newKey.version,
            timestamp: new Date()
        });

        return newKey;
    }

    async getKey(keyId, version = 'latest') {
        this.validateAccess(keyId);

        const keyRecord = this.keys.get(keyId);
        if (!keyRecord) {
            throw new Error(`Key not found: ${keyId}`);
        }

        if (!keyRecord.isActive) {
            throw new Error(`Key is not active: ${keyId}`);
        }

        // Update usage statistics
        keyRecord.lastUsed = new Date();
        keyRecord.usageCount++;

        this.audit('KEY_ACCESSED', { keyId, version });

        return this.serializeKeyRecord(keyRecord);
    }

    async revokeKey(keyId) {
        const keyRecord = this.keys.get(keyId);
        if (!keyRecord) {
            throw new Error(`Key not found: ${keyId}`);
        }

        keyRecord.isActive = false;
        keyRecord.revokedAt = new Date();

        this.audit('KEY_REVOKED', { keyId });

        this.emit('keyRevoked', {
            keyId,
            timestamp: new Date()
        });

        return keyRecord;
    }

    async restoreKey(keyId, version = null) {
        const keyRecord = this.keys.get(keyId);
        if (!keyRecord) {
            throw new Error(`Key not found: ${keyId}`);
        }

        if (version) {
            // Restore specific version
            const versions = this.keyVersions.get(keyId);
            const targetVersion = versions.find(v => v.version === version);
            
            if (!targetVersion) {
                throw new Error(`Version ${version} not found for key ${keyId}`);
            }

            this.keys.set(keyId, this.deserializeKeyRecord(targetVersion));
        } else {
            // Restore current key
            keyRecord.isActive = true;
            keyRecord.restoredAt = new Date();
        }

        this.audit('KEY_RESTORED', { keyId, version });

        this.emit('keyRestored', {
            keyId,
            version,
            timestamp: new Date()
        });

        return this.keys.get(keyId);
    }

    // Encryption and Decryption Methods
    async encrypt(keyId, plaintext, additionalData = null) {
        const keyRecord = await this.getKey(keyId);
        const decryptedKey = this.decryptKeyData(keyRecord.keyData);

        let encrypted;
        
        switch (keyRecord.keyType) {
            case 'aes':
                encrypted = await this.encryptAES(decryptedKey, plaintext, additionalData);
                break;
            case 'rsa':
                encrypted = await this.encryptRSA(decryptedKey, plaintext);
                break;
            default:
                throw new Error(`Encryption not supported for key type: ${keyRecord.keyType}`);
        }

        this.audit('DATA_ENCRYPTED', { 
            keyId, 
            dataSize: plaintext.length,
            algorithm: keyRecord.keyType 
        });

        return encrypted;
    }

    async decrypt(keyId, ciphertext, additionalData = null) {
        const keyRecord = await this.getKey(keyId);
        const decryptedKey = this.decryptKeyData(keyRecord.keyData);

        let decrypted;
        
        switch (keyRecord.keyType) {
            case 'aes':
                decrypted = await this.decryptAES(decryptedKey, ciphertext, additionalData);
                break;
            case 'rsa':
                decrypted = await this.decryptRSA(decryptedKey, ciphertext);
                break;
            default:
                throw new Error(`Decryption not supported for key type: ${keyRecord.keyType}`);
        }

        this.audit('DATA_DECRYPTED', { 
            keyId, 
            dataSize: ciphertext.length,
            algorithm: keyRecord.keyType 
        });

        return decrypted;
    }

    async encryptAES(key, plaintext, additionalData = null) {
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(key, 'base64'), iv);

        if (additionalData) {
            cipher.setAAD(Buffer.from(additionalData));
        }

        let encrypted = cipher.update(plaintext, 'utf8', 'base64');
        encrypted += cipher.final('base64');

        const authTag = cipher.getAuthTag();

        return {
            iv: iv.toString('base64'),
            data: encrypted,
            authTag: authTag.toString('base64'),
            additionalData: additionalData
        };
    }

    async decryptAES(key, ciphertext, additionalData = null) {
        const decipher = crypto.createDecipheriv(
            'aes-256-gcm', 
            Buffer.from(key, 'base64'), 
            Buffer.from(ciphertext.iv, 'base64')
        );

        decipher.setAuthTag(Buffer.from(ciphertext.authTag, 'base64'));

        if (additionalData) {
            decipher.setAAD(Buffer.from(additionalData));
        }

        let decrypted = decipher.update(ciphertext.data, 'base64', 'utf8');
        decrypted += decipher.final('utf8');

        return decrypted;
    }

    async encryptRSA(key, plaintext) {
        // Simplified RSA encryption
        const encrypted = crypto.publicEncrypt(
            {
                key: key,
                padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
                oaepHash: 'sha256'
            },
            Buffer.from(plaintext, 'utf8')
        );

        return encrypted.toString('base64');
    }

    async decryptRSA(key, ciphertext) {
        // Simplified RSA decryption
        const decrypted = crypto.privateDecrypt(
            {
                key: key,
                padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
                oaepHash: 'sha256'
            },
            Buffer.from(ciphertext, 'base64')
        );

        return decrypted.toString('utf8');
    }

    // Digital Signatures
    async sign(keyId, data) {
        const keyRecord = await this.getKey(keyId);
        const decryptedKey = this.decryptKeyData(keyRecord.keyData);

        let signature;
        
        switch (keyRecord.keyType) {
            case 'rsa':
                signature = this.signRSA(decryptedKey, data);
                break;
            case 'ec':
                signature = this.signEC(decryptedKey, data);
                break;
            case 'hmac':
                signature = this.signHMAC(decryptedKey, data);
                break;
            default:
                throw new Error(`Signing not supported for key type: ${keyRecord.keyType}`);
        }

        this.audit('DATA_SIGNED', { 
            keyId, 
            dataSize: data.length,
            algorithm: keyRecord.keyType 
        });

        return signature;
    }

    async verify(keyId, data, signature) {
        const keyRecord = await this.getKey(keyId);
        
        let isValid = false;
        
        switch (keyRecord.keyType) {
            case 'rsa':
                isValid = this.verifyRSA(keyRecord.publicKey, data, signature);
                break;
            case 'ec':
                isValid = this.verifyEC(keyRecord.publicKey, data, signature);
                break;
            case 'hmac':
                const decryptedKey = this.decryptKeyData(keyRecord.keyData);
                isValid = this.verifyHMAC(decryptedKey, data, signature);
                break;
            default:
                throw new Error(`Verification not supported for key type: ${keyRecord.keyType}`);
        }

        this.audit('SIGNATURE_VERIFIED', { 
            keyId, 
            isValid,
            algorithm: keyRecord.keyType 
        });

        return isValid;
    }

    signRSA(privateKey, data) {
        const sign = crypto.createSign('SHA256');
        sign.update(data);
        sign.end();
        return sign.sign(privateKey, 'base64');
    }

    verifyRSA(publicKey, data, signature) {
        const verify = crypto.createVerify('SHA256');
        verify.update(data);
        verify.end();
        return verify.verify(publicKey, signature, 'base64');
    }

    signEC(privateKey, data) {
        const sign = crypto.createSign('SHA256');
        sign.update(data);
        sign.end();
        return sign.sign(privateKey, 'base64');
    }

    verifyEC(publicKey, data, signature) {
        const verify = crypto.createVerify('SHA256');
        verify.update(data);
        verify.end();
        return verify.verify(publicKey, signature, 'base64');
    }

    signHMAC(key, data) {
        const hmac = crypto.createHmac('SHA256', Buffer.from(key, 'base64'));
        hmac.update(data);
        return hmac.digest('base64');
    }

    verifyHMAC(key, data, signature) {
        const expectedSignature = this.signHMAC(key, data);
        return crypto.timingSafeEqual(
            Buffer.from(expectedSignature, 'base64'),
            Buffer.from(signature, 'base64')
        );
    }

    // Security and Access Control
    validateAccess(keyId) {
        if (this.lockedKeys.has(keyId)) {
            throw new Error(`Key is temporarily locked: ${keyId}`);
        }

        // Check access policies
        const policy = this.accessPolicies.get(keyId);
        if (policy && !this.checkAccessPolicy(policy)) {
            this.recordFailedAttempt(keyId);
            throw new Error(`Access denied for key: ${keyId}`);
        }

        // Reset failed attempts on successful access
        this.failedAttempts.delete(keyId);
    }

    recordFailedAttempt(keyId) {
        const attempts = this.failedAttempts.get(keyId) || 0;
        const newAttempts = attempts + 1;
        
        this.failedAttempts.set(keyId, newAttempts);

        if (newAttempts >= this.securityConfig.accessControl.maxAttempts) {
            this.lockKey(keyId);
            throw new Error(`Key ${keyId} has been locked due to too many failed attempts`);
        }
    }

    lockKey(keyId) {
        this.lockedKeys.add(keyId);
        
        setTimeout(() => {
            this.lockedKeys.delete(keyId);
            this.failedAttempts.delete(keyId);
        }, this.securityConfig.accessControl.lockoutDuration);

        this.audit('KEY_LOCKED', { keyId, duration: this.securityConfig.accessControl.lockoutDuration });
    }

    checkAccessPolicy(policy) {
        // Simplified access policy check
        // In production, this would check user roles, time-based restrictions, etc.
        return true;
    }

    setAccessPolicy(keyId, policy) {
        this.accessPolicies.set(keyId, policy);
        this.audit('ACCESS_POLICY_UPDATED', { keyId, policy });
    }

    // Key Encryption and Protection
    encryptKeyData(keyData) {
        // In a real implementation, this would use a proper key encryption key (KEK)
        // This is a simplified version for demonstration
        const cipher = crypto.createCipher('aes-256-gcm', this.encryptionKey);
        let encrypted = cipher.update(keyData, 'utf8', 'base64');
        encrypted += cipher.final('base64');
        return encrypted;
    }

    decryptKeyData(encryptedKeyData) {
        // Decrypt key data using the master encryption key
        const decipher = crypto.createDecipher('aes-256-gcm', this.encryptionKey);
        let decrypted = decipher.update(encryptedKeyData, 'base64', 'utf8');
        decrypted += decipher.final('utf8');
        return decrypted;
    }

    generateEncryptionKey() {
        return crypto.randomBytes(32); // 256-bit key
    }

    // Audit and Monitoring
    audit(action, details) {
        const auditEntry = {
            timestamp: new Date(),
            action,
            details,
            vault: this.vaultName
        };

        this.auditLog.push(auditEntry);

        // Keep only recent audit entries (last 10,000)
        if (this.auditLog.length > 10000) {
            this.auditLog = this.auditLog.slice(-5000);
        }

        this.emit('audit', auditEntry);
    }

    getAuditLog(filters = {}) {
        let filteredLog = this.auditLog;

        if (filters.startDate) {
            filteredLog = filteredLog.filter(entry => entry.timestamp >= filters.startDate);
        }

        if (filters.endDate) {
            filteredLog = filteredLog.filter(entry => entry.timestamp <= filters.endDate);
        }

        if (filters.action) {
            filteredLog = filteredLog.filter(entry => entry.action === filters.action);
        }

        return filteredLog;
    }

    // Key Inventory and Management
    listKeys(filters = {}) {
        let keys = Array.from(this.keys.values());

        if (filters.keyType) {
            keys = keys.filter(key => key.keyType === filters.keyType);
        }

        if (filters.active !== undefined) {
            keys = keys.filter(key => key.isActive === filters.active);
        }

        return keys.map(key => this.serializeKeyRecord(key));
    }

    getKeyStatistics() {
        const keys = Array.from(this.keys.values());
        
        return {
            totalKeys: keys.length,
            activeKeys: keys.filter(k => k.isActive).length,
            byType: this.groupBy(keys, 'keyType'),
            bySize: this.groupBy(keys, 'keySize'),
            expiringSoon: keys.filter(k => 
                new Date(k.expiresAt) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
            ).length
        };
    }

    groupBy(array, key) {
        return array.reduce((groups, item) => {
            const val = item[key];
            groups[val] = groups[val] || [];
            groups[val].push(item);
            return groups;
        }, {});
    }

    // Serialization and Deserialization
    serializeKeyRecord(keyRecord) {
        // Create a safe serializable version without sensitive data
        return {
            keyId: keyRecord.keyId,
            keyType: keyRecord.keyType,
            keySize: keyRecord.keySize,
            version: keyRecord.version,
            createdAt: keyRecord.createdAt,
            lastUsed: keyRecord.lastUsed,
            expiresAt: keyRecord.expiresAt,
            isActive: keyRecord.isActive,
            usageCount: keyRecord.usageCount,
            metadata: keyRecord.metadata,
            // Note: keyData and publicKey are not included for security
        };
    }

    deserializeKeyRecord(serialized) {
        // This would reconstruct the full key record from serialized data
        // In practice, you'd need to store the encrypted key data separately
        return serialized;
    }

    // Backup and Recovery
    async createBackup() {
        const backupData = {
            vaultName: this.vaultName,
            timestamp: new Date(),
            keys: Array.from(this.keys.entries()),
            keyVersions: Array.from(this.keyVersions.entries()),
            securityConfig: this.securityConfig
        };

        // Encrypt the backup
        const encryptedBackup = await this.encrypt('backup-key', JSON.stringify(backupData));

        this.audit('BACKUP_CREATED', { 
            keyCount: this.keys.size,
            timestamp: new Date() 
        });

        return encryptedBackup;
    }

    async restoreBackup(encryptedBackup) {
        const backupData = JSON.parse(await this.decrypt('backup-key', encryptedBackup));

        // Validate backup
        if (backupData.vaultName !== this.vaultName) {
            throw new Error('Backup vault name mismatch');
        }

        // Restore data
        this.keys = new Map(backupData.keys);
        this.keyVersions = new Map(backupData.keyVersions);
        this.securityConfig = backupData.securityConfig;

        this.audit('BACKUP_RESTORED', { 
            keyCount: this.keys.size,
            timestamp: new Date() 
        });

        return true;
    }
}

module.exports = KeyVaultManager;

// Example usage
if (require.main === module) {
    const keyVault = new KeyVaultManager('main-vault');
    
    // Set up event listeners
    keyVault.on('keyGenerated', (data) => {
        console.log('Key generated:', data.keyId);
    });
    
    keyVault.on('audit', (entry) => {
        console.log('Audit:', entry.action, entry.timestamp);
    });
    
    // Demo sequence
    async function demo() {
        try {
            // Generate a new AES key
            const aesKey = await keyVault.generateKey('encryption-key', 'aes', 256, {
                purpose: 'data-encryption',
                environment: 'production'
            });
            
            console.log('AES Key generated:', aesKey.keyId);
            
            // Generate an RSA key pair
            const rsaKey = await keyVault.generateKey('signing-key', 'rsa', 2048, {
                purpose: 'digital-signatures',
                algorithm: 'RSA-PSS'
            });
            
            console.log('RSA Key generated:', rsaKey.keyId);
            
            // Encrypt some data
            const plaintext = 'Sensitive data that needs protection';
            const encrypted = await keyVault.encrypt('encryption-key', plaintext);
            
            console.log('Data encrypted successfully');
            
            // Decrypt the data
            const decrypted = await keyVault.decrypt('encryption-key', encrypted);
            
            console.log('Data decrypted successfully:', decrypted === plaintext);
            
            // Sign some data
            const dataToSign = 'Important document content';
            const signature = await keyVault.sign('signing-key', dataToSign);
            
            console.log('Data signed successfully');
            
            // Verify the signature
            const isValid = await keyVault.verify('signing-key', dataToSign, signature);
            
            console.log('Signature verified:', isValid);
            
            // Get key statistics
            const stats = keyVault.getKeyStatistics();
            console.log('Key statistics:', stats);
            
            // Create a backup
            const backup = await keyVault.createBackup();
            console.log('Backup created successfully');
            
        } catch (error) {
            console.error('Demo error:', error);
        }
    }
    
    demo();
}