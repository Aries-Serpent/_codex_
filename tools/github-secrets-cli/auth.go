package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/zalando/go-keyring"
)

const (
	keyringService  = "github-secrets-cli"
	keyringUser     = "default"
	githubOAuthURL  = "https://github.com/login/device/code"
	githubTokenURL  = "https://github.com/login/oauth/access_token"
	githubClientID  = "Iv1.b507a08c87ecfe98" // GitHub CLI client ID (public)
)

// AuthManager handles authentication and token management
type AuthManager struct {
	token string
}

// NewAuthManager creates a new auth manager
func NewAuthManager() *AuthManager {
	return &AuthManager{}
}

// GetToken retrieves the auth token from env var or keyring
func (a *AuthManager) GetToken() (string, error) {
	// First check environment variable
	if token := getEnvToken(); token != "" {
		a.token = token
		return token, nil
	}

	// Try to get from keyring
	token, err := keyring.Get(keyringService, keyringUser)
	if err != nil {
		return "", fmt.Errorf("no authentication token found. Run 'auth login' or set GITHUB_TOKEN")
	}

	a.token = token
	return token, nil
}

// LoginDeviceFlow performs OAuth2 device flow login
func (a *AuthManager) LoginDeviceFlow(ctx context.Context) error {
	// Request device code
	deviceCode, err := a.requestDeviceCode(ctx)
	if err != nil {
		return fmt.Errorf("failed to request device code: %w", err)
	}

	fmt.Printf("Please visit: %s\n", deviceCode.VerificationURI)
	fmt.Printf("Enter code: %s\n", deviceCode.UserCode)
	fmt.Println("Waiting for authentication...")

	// Poll for token
	token, err := a.pollForToken(ctx, deviceCode)
	if err != nil {
		return fmt.Errorf("failed to obtain token: %w", err)
	}

	// Store token in keyring
	if err := keyring.Set(keyringService, keyringUser, token); err != nil {
		return fmt.Errorf("failed to store token: %w", err)
	}

	a.token = token
	fmt.Println("✅ Authentication successful!")
	return nil
}

// LoginWithPAT stores a Personal Access Token
func (a *AuthManager) LoginWithPAT(token string) error {
	// Validate token
	if !strings.HasPrefix(token, "ghp_") && !strings.HasPrefix(token, "github_pat_") {
		return fmt.Errorf("invalid token format. Expected ghp_* or github_pat_*")
	}

	// Store in keyring
	if err := keyring.Set(keyringService, keyringUser, token); err != nil {
		return fmt.Errorf("failed to store token: %w", err)
	}

	a.token = token
	fmt.Println("✅ Token stored successfully!")
	return nil
}

// Logout removes stored credentials
func (a *AuthManager) Logout() error {
	if err := keyring.Delete(keyringService, keyringUser); err != nil {
		return fmt.Errorf("failed to delete token: %w", err)
	}

	a.token = ""
	fmt.Println("✅ Logged out successfully!")
	return nil
}

// Status shows authentication status
func (a *AuthManager) Status() error {
	token, err := a.GetToken()
	if err != nil {
		fmt.Println("❌ Not authenticated")
		return err
	}

	// Validate token against GitHub API
	if err := a.validateToken(token); err != nil {
		fmt.Println("❌ Token is invalid or expired")
		return err
	}

	// Mask token for display
	masked := maskToken(token)
	fmt.Printf("✅ Authenticated (token: %s)\n", masked)
	return nil
}

// ValidateToken checks if token is valid
func (a *AuthManager) validateToken(token string) error {
	req, err := http.NewRequest("GET", apiBaseURL+"/user", nil)
	if err != nil {
		return err
	}

	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("invalid token (status: %d)", resp.StatusCode)
	}

	return nil
}

// Device code response structure
type deviceCodeResponse struct {
	DeviceCode      string `json:"device_code"`
	UserCode        string `json:"user_code"`
	VerificationURI string `json:"verification_uri"`
	ExpiresIn       int    `json:"expires_in"`
	Interval        int    `json:"interval"`
}

// requestDeviceCode initiates the device flow
func (a *AuthManager) requestDeviceCode(ctx context.Context) (*deviceCodeResponse, error) {
	data := strings.NewReader(fmt.Sprintf("client_id=%s&scope=repo,admin:org,codespace", githubClientID))
	
	req, err := http.NewRequestWithContext(ctx, "POST", githubOAuthURL, data)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Accept", "application/json")
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("failed to get device code (status %d): %s", resp.StatusCode, string(body))
	}

	var result deviceCodeResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

// Token response structure
type tokenResponse struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
	Scope       string `json:"scope"`
	Error       string `json:"error"`
}

// pollForToken polls for the access token
func (a *AuthManager) pollForToken(ctx context.Context, deviceCode *deviceCodeResponse) (string, error) {
	interval := time.Duration(deviceCode.Interval) * time.Second
	if interval < 5*time.Second {
		interval = 5 * time.Second
	}

	timeout := time.Duration(deviceCode.ExpiresIn) * time.Second
	deadline := time.Now().Add(timeout)

	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return "", ctx.Err()
		case <-ticker.C:
			if time.Now().After(deadline) {
				return "", fmt.Errorf("device code expired")
			}

			token, err := a.checkToken(ctx, deviceCode.DeviceCode)
			if err != nil {
				if err.Error() == "authorization_pending" {
					continue // Keep polling
				}
				return "", err
			}

			return token, nil
		}
	}
}

// checkToken checks if the token is available
func (a *AuthManager) checkToken(ctx context.Context, deviceCode string) (string, error) {
	data := strings.NewReader(fmt.Sprintf("client_id=%s&device_code=%s&grant_type=urn:ietf:params:oauth:grant-type:device_code", githubClientID, deviceCode))
	
	req, err := http.NewRequestWithContext(ctx, "POST", githubTokenURL, data)
	if err != nil {
		return "", err
	}

	req.Header.Set("Accept", "application/json")
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var result tokenResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	if result.Error != "" {
		return "", fmt.Errorf(result.Error)
	}

	if result.AccessToken == "" {
		return "", fmt.Errorf("no access token received")
	}

	return result.AccessToken, nil
}

// Helper functions

func getEnvToken() string {
	return os.Getenv("GITHUB_TOKEN")
}

func maskToken(token string) string {
	if len(token) < 8 {
		return "***"
	}
	return token[:4] + "..." + token[len(token)-4:]
}
