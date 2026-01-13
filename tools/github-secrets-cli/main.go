package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/spf13/cobra"
)

const (
	serviceName = "github-secrets-cli"
	apiBaseURL  = "https://api.github.com"
)

var (
	// version is displayed with --version flag
	// Update this for each release
	version = "1.0.0"
)

// Root command
var rootCmd = &cobra.Command{
	Use:   "github-secrets-cli",
	Short: "Manage GitHub secrets across different scopes",
	Long: `A command-line tool for managing GitHub secrets across organization, repository, 
environment, and Codespaces scopes with client-side encryption and secure authentication.`,
	Version: version,
}

func init() {
	rootCmd.AddCommand(authCmd)
	rootCmd.AddCommand(setCmd)
	rootCmd.AddCommand(listCmd)
	rootCmd.AddCommand(deleteCmd)
	rootCmd.AddCommand(auditCmd)
}

// auth command with subcommands
var authCmd = &cobra.Command{
	Use:   "auth",
	Short: "Authentication commands",
}

var authLoginCmd = &cobra.Command{
	Use:   "login",
	Short: "Login using OAuth2 device flow or PAT",
	RunE: func(cmd *cobra.Command, args []string) error {
		token, _ := cmd.Flags().GetString("token")
		authMgr := NewAuthManager()
		
		if token != "" {
			return authMgr.LoginWithPAT(token)
		}
		
		return authMgr.LoginDeviceFlow(context.Background())
	},
}

var authLogoutCmd = &cobra.Command{
	Use:   "logout",
	Short: "Logout and remove stored credentials",
	RunE: func(cmd *cobra.Command, args []string) error {
		authMgr := NewAuthManager()
		return authMgr.Logout()
	},
}

var authStatusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show authentication status",
	RunE: func(cmd *cobra.Command, args []string) error {
		authMgr := NewAuthManager()
		return authMgr.Status()
	},
}

// set command
var setCmd = &cobra.Command{
	Use:   "set",
	Short: "Set a secret",
	RunE: func(cmd *cobra.Command, args []string) error {
		scope, _ := cmd.Flags().GetString("scope")
		owner, _ := cmd.Flags().GetString("owner")
		repo, _ := cmd.Flags().GetString("repo")
		org, _ := cmd.Flags().GetString("org")
		env, _ := cmd.Flags().GetString("env")
		name, _ := cmd.Flags().GetString("name")
		value, _ := cmd.Flags().GetString("value")
		visibility, _ := cmd.Flags().GetString("visibility")
		selectedRepos, _ := cmd.Flags().GetStringSlice("selected-repos")

		// Validate required flags
		if name == "" || value == "" {
			return fmt.Errorf("--name and --value are required")
		}

		// Determine owner from org or repo
		if org != "" {
			owner = org
		} else if repo != "" && owner == "" {
			parts := strings.Split(repo, "/")
			if len(parts) == 2 {
				owner = parts[0]
				repo = parts[1]
			} else {
				return fmt.Errorf("--repo must be in format owner/repo or specify --owner")
			}
		}

		// Get auth token
		authMgr := NewAuthManager()
		token, err := authMgr.GetToken()
		if err != nil {
			return err
		}

		// Create client and set secret
		client := NewGitHubClient(token)
		if err := client.SetSecret(scope, owner, repo, env, name, value, visibility, selectedRepos); err != nil {
			return err
		}

		fmt.Printf("✅ Secret '%s' set successfully!\n", name)
		return nil
	},
}

// list command
var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List secrets",
	RunE: func(cmd *cobra.Command, args []string) error {
		scope, _ := cmd.Flags().GetString("scope")
		owner, _ := cmd.Flags().GetString("owner")
		repo, _ := cmd.Flags().GetString("repo")
		org, _ := cmd.Flags().GetString("org")
		env, _ := cmd.Flags().GetString("env")

		// Determine owner
		if org != "" {
			owner = org
		} else if repo != "" && owner == "" {
			parts := strings.Split(repo, "/")
			if len(parts) == 2 {
				owner = parts[0]
				repo = parts[1]
			} else {
				return fmt.Errorf("--repo must be in format owner/repo or specify --owner")
			}
		}

		// Get auth token
		authMgr := NewAuthManager()
		token, err := authMgr.GetToken()
		if err != nil {
			return err
		}

		// Create client and list secrets
		client := NewGitHubClient(token)
		secrets, err := client.ListSecrets(scope, owner, repo, env)
		if err != nil {
			return err
		}

		// Print secrets
		fmt.Printf("Found %d secret(s):\n", len(secrets))
		for _, secret := range secrets {
			fmt.Printf("  - %s (updated: %s)\n", secret.Name, secret.UpdatedAt.Format(time.RFC3339))
		}

		return nil
	},
}

// delete command
var deleteCmd = &cobra.Command{
	Use:   "delete",
	Short: "Delete a secret",
	RunE: func(cmd *cobra.Command, args []string) error {
		scope, _ := cmd.Flags().GetString("scope")
		owner, _ := cmd.Flags().GetString("owner")
		repo, _ := cmd.Flags().GetString("repo")
		org, _ := cmd.Flags().GetString("org")
		env, _ := cmd.Flags().GetString("env")
		name, _ := cmd.Flags().GetString("name")
		confirm, _ := cmd.Flags().GetBool("yes")

		// Validate required flags
		if name == "" {
			return fmt.Errorf("--name is required")
		}

		// Determine owner
		if org != "" {
			owner = org
		} else if repo != "" && owner == "" {
			parts := strings.Split(repo, "/")
			if len(parts) == 2 {
				owner = parts[0]
				repo = parts[1]
			} else {
				return fmt.Errorf("--repo must be in format owner/repo or specify --owner")
			}
		}

		// Confirmation prompt
		if !confirm {
			fmt.Printf("Are you sure you want to delete secret '%s'? (y/N): ", name)
			var response string
			fmt.Scanln(&response)
			if strings.ToLower(response) != "y" {
				fmt.Println("Cancelled")
				return nil
			}
		}

		// Get auth token
		authMgr := NewAuthManager()
		token, err := authMgr.GetToken()
		if err != nil {
			return err
		}

		// Create client and delete secret
		client := NewGitHubClient(token)
		if err := client.DeleteSecret(scope, owner, repo, env, name); err != nil {
			return err
		}

		fmt.Printf("✅ Secret '%s' deleted successfully!\n", name)
		return nil
	},
}

// audit command
var auditCmd = &cobra.Command{
	Use:   "audit",
	Short: "Get secret metadata and audit information",
	RunE: func(cmd *cobra.Command, args []string) error {
		scope, _ := cmd.Flags().GetString("scope")
		owner, _ := cmd.Flags().GetString("owner")
		repo, _ := cmd.Flags().GetString("repo")
		org, _ := cmd.Flags().GetString("org")
		env, _ := cmd.Flags().GetString("env")
		format, _ := cmd.Flags().GetString("format")

		// Determine owner
		if org != "" {
			owner = org
		} else if repo != "" && owner == "" {
			parts := strings.Split(repo, "/")
			if len(parts) == 2 {
				owner = parts[0]
				repo = parts[1]
			} else {
				return fmt.Errorf("--repo must be in format owner/repo or specify --owner")
			}
		}

		// Get auth token
		authMgr := NewAuthManager()
		token, err := authMgr.GetToken()
		if err != nil {
			return err
		}

		// Create client and list secrets for audit
		client := NewGitHubClient(token)
		secrets, err := client.ListSecrets(scope, owner, repo, env)
		if err != nil {
			return err
		}

		// Create audit report
		auditReport := map[string]interface{}{
			"scope":        scope,
			"owner":        owner,
			"repo":         repo,
			"environment":  env,
			"timestamp":    time.Now().Format(time.RFC3339),
			"total_count":  len(secrets),
			"secrets":      secrets,
		}

		// Output in requested format
		if format == "json" {
			output, _ := json.MarshalIndent(auditReport, "", "  ")
			fmt.Println(string(output))
		} else {
			fmt.Printf("Audit Report (%s)\n", auditReport["timestamp"])
			fmt.Printf("Scope: %s\n", scope)
			if owner != "" {
				fmt.Printf("Owner: %s\n", owner)
			}
			if repo != "" {
				fmt.Printf("Repository: %s\n", repo)
			}
			if env != "" {
				fmt.Printf("Environment: %s\n", env)
			}
			fmt.Printf("Total Secrets: %d\n", len(secrets))
		}

		return nil
	},
}

func init() {
	// auth subcommands
	authCmd.AddCommand(authLoginCmd)
	authCmd.AddCommand(authLogoutCmd)
	authCmd.AddCommand(authStatusCmd)
	authLoginCmd.Flags().String("token", "", "Personal Access Token (alternative to device flow)")

	// set command flags
	setCmd.Flags().String("scope", "repo", "Secret scope (repo, org, env, user)")
	setCmd.Flags().String("owner", "", "Repository owner or organization name")
	setCmd.Flags().String("repo", "", "Repository name (format: owner/repo)")
	setCmd.Flags().String("org", "", "Organization name (alternative to --owner)")
	setCmd.Flags().String("env", "", "Environment name (for env scope)")
	setCmd.Flags().String("name", "", "Secret name (required)")
	setCmd.Flags().String("value", "", "Secret value (required)")
	setCmd.Flags().String("visibility", "private", "Visibility for org secrets (private, all, selected)")
	setCmd.Flags().StringSlice("selected-repos", []string{}, "Selected repositories for org secrets")

	// list command flags
	listCmd.Flags().String("scope", "repo", "Secret scope (repo, org, env, user)")
	listCmd.Flags().String("owner", "", "Repository owner or organization name")
	listCmd.Flags().String("repo", "", "Repository name (format: owner/repo)")
	listCmd.Flags().String("org", "", "Organization name (alternative to --owner)")
	listCmd.Flags().String("env", "", "Environment name (for env scope)")

	// delete command flags
	deleteCmd.Flags().String("scope", "repo", "Secret scope (repo, org, env, user)")
	deleteCmd.Flags().String("owner", "", "Repository owner or organization name")
	deleteCmd.Flags().String("repo", "", "Repository name (format: owner/repo)")
	deleteCmd.Flags().String("org", "", "Organization name (alternative to --owner)")
	deleteCmd.Flags().String("env", "", "Environment name (for env scope)")
	deleteCmd.Flags().String("name", "", "Secret name (required)")
	deleteCmd.Flags().Bool("yes", false, "Skip confirmation prompt")

	// audit command flags
	auditCmd.Flags().String("scope", "repo", "Secret scope (repo, org, env, user)")
	auditCmd.Flags().String("owner", "", "Repository owner or organization name")
	auditCmd.Flags().String("repo", "", "Repository name (format: owner/repo)")
	auditCmd.Flags().String("org", "", "Organization name (alternative to --owner)")
	auditCmd.Flags().String("env", "", "Environment name (for env scope)")
	auditCmd.Flags().String("format", "text", "Output format (text, json)")
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
