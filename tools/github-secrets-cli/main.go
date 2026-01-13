package main

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/spf13/cobra"
	"github.com/zalando/go-keyring"
	"golang.org/x/crypto/nacl/box"
	"golang.org/x/oauth2"
)

const (
	serviceName = "github-secrets-cli"
	apiBaseURL  = "https://api.github.com"
)

var (
	version = "1.0.0"
)

// Root command
var rootCmd = &cobra.Command{
	Use:   "github-secrets-cli",
	Short: "Manage GitHub secrets across different scopes",
	Long: `A command-line tool for managing GitHub secrets across organization, repository, 
environment, and Codespaces scopes with client-side encryption and secure authentication.`,
	Version: "1.0.0",
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
