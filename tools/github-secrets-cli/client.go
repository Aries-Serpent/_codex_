package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// GitHubClient handles GitHub API operations
type GitHubClient struct {
	client    *http.Client
	token     string
	encryptor *EncryptionManager
}

// NewGitHubClient creates a new GitHub API client
func NewGitHubClient(token string) *GitHubClient {
	return &GitHubClient{
		client:    &http.Client{Timeout: 30 * time.Second},
		token:     token,
		encryptor: NewEncryptionManager(token),
	}
}

// SecretRequest represents a request to create/update a secret
type SecretRequest struct {
	EncryptedValue string `json:"encrypted_value"`
	KeyID          string `json:"key_id"`
	Visibility     string `json:"visibility,omitempty"`      // For org secrets
	SelectedRepoIDs []int `json:"selected_repository_ids,omitempty"` // For org secrets
}

// SecretInfo represents information about a secret
type SecretInfo struct {
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// SecretsListResponse represents a list of secrets
type SecretsListResponse struct{
	TotalCount int          `json:"total_count"`
	Secrets    []SecretInfo `json:"secrets"`
}

// SetSecret creates or updates a secret
func (c *GitHubClient) SetSecret(scope, owner, repo, env, name, value string, visibility string, selectedRepos []string) error {
	// Get public key for encryption
	pubKey, err := c.encryptor.GetPublicKey(scope, owner, repo, env)
	if err != nil {
		return fmt.Errorf("failed to get public key: %w", err)
	}

	// Encrypt the secret value
	encryptedValue, err := c.encryptor.EncryptSecret(value, pubKey.Key)
	if err != nil {
		return fmt.Errorf("failed to encrypt secret: %w", err)
	}

	// Prepare request body
	secretReq := SecretRequest{
		EncryptedValue: encryptedValue,
		KeyID:          pubKey.KeyID,
	}

	// Add visibility for org secrets
	if scope == "org" && visibility != "" {
		secretReq.Visibility = visibility
	}

	// Build URL based on scope
	var url string
	switch scope {
	case "repo":
		url = fmt.Sprintf("%s/repos/%s/%s/actions/secrets/%s", apiBaseURL, owner, repo, name)
	case "org":
		url = fmt.Sprintf("%s/orgs/%s/actions/secrets/%s", apiBaseURL, owner, name)
	case "env":
		// Need to get repository ID first
		repoID, err := c.getRepositoryID(owner, repo)
		if err != nil {
			return fmt.Errorf("failed to get repository ID: %w", err)
		}
		url = fmt.Sprintf("%s/repositories/%d/environments/%s/secrets/%s", apiBaseURL, repoID, env, name)
	case "user":
		url = fmt.Sprintf("%s/user/codespaces/secrets/%s", apiBaseURL, name)
	default:
		return fmt.Errorf("unsupported scope: %s", scope)
	}

	// Marshal request body
	body, err := json.Marshal(secretReq)
	if err != nil {
		return err
	}

	// Make PUT request
	req, err := http.NewRequest("PUT", url, bytes.NewReader(body))
	if err != nil {
		return err
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusNoContent {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("failed to set secret (status %d): %s", resp.StatusCode, string(body))
	}

	return nil
}

// ListSecrets lists secrets for a given scope
func (c *GitHubClient) ListSecrets(scope, owner, repo, env string) ([]SecretInfo, error) {
	var url string
	
	switch scope {
	case "repo":
		url = fmt.Sprintf("%s/repos/%s/%s/actions/secrets", apiBaseURL, owner, repo)
	case "org":
		url = fmt.Sprintf("%s/orgs/%s/actions/secrets", apiBaseURL, owner)
	case "env":
		repoID, err := c.getRepositoryID(owner, repo)
		if err != nil {
			return nil, fmt.Errorf("failed to get repository ID: %w", err)
		}
		url = fmt.Sprintf("%s/repositories/%d/environments/%s/secrets", apiBaseURL, repoID, env)
	case "user":
		url = fmt.Sprintf("%s/user/codespaces/secrets", apiBaseURL)
	default:
		return nil, fmt.Errorf("unsupported scope: %s", scope)
	}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("failed to list secrets (status %d): %s", resp.StatusCode, string(body))
	}

	var result SecretsListResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return result.Secrets, nil
}

// DeleteSecret deletes a secret
func (c *GitHubClient) DeleteSecret(scope, owner, repo, env, name string) error {
	var url string
	
	switch scope {
	case "repo":
		url = fmt.Sprintf("%s/repos/%s/%s/actions/secrets/%s", apiBaseURL, owner, repo, name)
	case "org":
		url = fmt.Sprintf("%s/orgs/%s/actions/secrets/%s", apiBaseURL, owner, name)
	case "env":
		repoID, err := c.getRepositoryID(owner, repo)
		if err != nil {
			return fmt.Errorf("failed to get repository ID: %w", err)
		}
		url = fmt.Sprintf("%s/repositories/%d/environments/%s/secrets/%s", apiBaseURL, repoID, env, name)
	case "user":
		url = fmt.Sprintf("%s/user/codespaces/secrets/%s", apiBaseURL, name)
	default:
		return fmt.Errorf("unsupported scope: %s", scope)
	}

	req, err := http.NewRequest("DELETE", url, nil)
	if err != nil {
		return err
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")

	resp, err := c.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNoContent {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("failed to delete secret (status %d): %s", resp.StatusCode, string(body))
	}

	return nil
}

// Repository represents a GitHub repository
type Repository struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

// getRepositoryID gets the ID of a repository
func (c *GitHubClient) getRepositoryID(owner, repo string) (int, error) {
	url := fmt.Sprintf("%s/repos/%s/%s", apiBaseURL, owner, repo)
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return 0, err
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")

	resp, err := c.client.Do(req)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return 0, fmt.Errorf("failed to get repository (status %d): %s", resp.StatusCode, string(body))
	}

	var repository Repository
	if err := json.NewDecoder(resp.Body).Decode(&repository); err != nil {
		return 0, err
	}

	return repository.ID, nil
}
