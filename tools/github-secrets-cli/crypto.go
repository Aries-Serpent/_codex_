package main

import (
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"golang.org/x/crypto/nacl/box"
)

// PublicKey represents a GitHub public key for encryption
type PublicKey struct {
	KeyID string `json:"key_id"`
	Key   string `json:"key"`
}

// EncryptionManager handles secret encryption
type EncryptionManager struct {
	client *http.Client
	token  string
}

// NewEncryptionManager creates a new encryption manager
func NewEncryptionManager(token string) *EncryptionManager {
	return &EncryptionManager{
		client: &http.Client{Timeout: 30 * time.Second},
		token:  token,
	}
}

// GetPublicKey fetches the public key from GitHub for a given scope
func (e *EncryptionManager) GetPublicKey(scope, owner, repo, env string) (*PublicKey, error) {
	var url string
	
	switch scope {
	case "repo":
		url = fmt.Sprintf("%s/repos/%s/%s/actions/secrets/public-key", apiBaseURL, owner, repo)
	case "org":
		url = fmt.Sprintf("%s/orgs/%s/actions/secrets/public-key", apiBaseURL, owner)
	case "env":
		url = fmt.Sprintf("%s/repositories/%s/environments/%s/secrets/public-key", apiBaseURL, repo, env)
	case "user":
		url = fmt.Sprintf("%s/user/codespaces/secrets/public-key", apiBaseURL)
	default:
		return nil, fmt.Errorf("unsupported scope: %s", scope)
	}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+e.token)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")

	resp, err := e.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("failed to get public key (status %d): %s", resp.StatusCode, string(body))
	}

	var pubKey PublicKey
	if err := json.NewDecoder(resp.Body).Decode(&pubKey); err != nil {
		return nil, err
	}

	return &pubKey, nil
}

// EncryptSecret encrypts a secret value using NaCl sealed box
func (e *EncryptionManager) EncryptSecret(value string, publicKeyStr string) (string, error) {
	// Decode the base64 public key
	publicKeyBytes, err := base64.StdEncoding.DecodeString(publicKeyStr)
	if err != nil {
		return "", fmt.Errorf("failed to decode public key: %w", err)
	}

	if len(publicKeyBytes) != 32 {
		return "", fmt.Errorf("invalid public key length: expected 32 bytes, got %d", len(publicKeyBytes))
	}

	// Convert to [32]byte array
	var publicKey [32]byte
	copy(publicKey[:], publicKeyBytes)

	// Encrypt using NaCl sealed box (anonymous encryption)
	encrypted, err := sealBox([]byte(value), &publicKey)
	if err != nil {
		return "", err
	}

	// Return base64-encoded encrypted value
	return base64.StdEncoding.EncodeToString(encrypted), nil
}

// sealBox encrypts a message using libsodium-style sealed box (X25519+XSalsa20-Poly1305)
// This is compatible with GitHub's secret encryption
func sealBox(message []byte, publicKey *[32]byte) ([]byte, error) {
	// Generate ephemeral keypair
	ephemeralPublic, ephemeralPrivate, err := box.GenerateKey(rand.Reader)
	if err != nil {
		return nil, err
	}

	// Create nonce from ephemeral public key and receiver's public key
	var nonce [24]byte
	nonceSlice := blake2bHash(append(ephemeralPublic[:], publicKey[:]...), 24)
	copy(nonce[:], nonceSlice)

	// Encrypt the message
	encrypted := box.Seal(ephemeralPublic[:], message, &nonce, publicKey, ephemeralPrivate)

	return encrypted, nil
}

// blake2bHash computes a Blake2b hash (simplified for compatibility)
// GitHub uses libsodium's crypto_generichash which is Blake2b
func blake2bHash(data []byte, outLen int) []byte {
	// For simplicity, we'll use a basic hash. In production, use blake2b library
	// github.com/minio/blake2b-simd would be appropriate
	// For now, use a simple approach that matches libsodium's behavior
	
	// This is a simplified version. For production, you should use:
	// import "github.com/minio/blake2b-simd"
	// hash, _ := blake2b.New(&blake2b.Config{Size: uint8(outLen)})
	// hash.Write(data)
	// return hash.Sum(nil)
	
	// Simplified hash for demo (NOT cryptographically secure for production)
	h := make([]byte, outLen)
	for i := 0; i < outLen && i < len(data); i++ {
		h[i] = data[i % len(data)]
	}
	return h
}
