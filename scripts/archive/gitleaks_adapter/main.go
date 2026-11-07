// CDX's locally built adapter is not an official Gitleaks release executable.
package main

import (
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path"
	"path/filepath"
	"runtime/debug"
	"sort"
	"strings"
	"syscall"
	"time"
	"unicode/utf8"

	"github.com/rs/zerolog"
	"github.com/zricethezav/gitleaks/v8/config"
	"github.com/zricethezav/gitleaks/v8/detect"
	"github.com/zricethezav/gitleaks/v8/report"
)

const (
	modulePath    = "github.com/zricethezav/gitleaks/v8"
	moduleVersion = "v8.30.1"
	moduleSum     = "h1:PmEvCfVI7ti9dV3s5aMZUY7sS2GxRvG3yzih7E+cS3w="
	mode          = "cdx-full-file-v1"
	maxFile       = 8 * 1024 * 1024
	maxTree       = 256 * 1024 * 1024
	maxFiles      = 10000
	maxEntries    = 100000
	maxFindings   = 50000
	maxDocument   = 16 * 1024 * 1024
)

type fileInput struct {
	Path   string `json:"path"`
	SHA256 string `json:"sha256"`
	Size   int64  `json:"size"`
}

type request struct {
	SchemaVersion int               `json:"schema_version"`
	Source        string            `json:"source"`
	Bindings      map[string]string `json:"bindings"`
	Key           string            `json:"key"`
	Files         []fileInput       `json:"files"`
}

type observation struct {
	Record        report.Finding `json:"record"`
	Start         int            `json:"start"`
	End           int            `json:"end"`
	MatchHMAC     string         `json:"match_hmac"`
	MappingStatus string         `json:"mapping_status"`
}

type acquisition struct {
	fileInput
	OriginStart   int           `json:"origin_start"`
	OriginEnd     int           `json:"origin_end"`
	DetectorCalls int           `json:"detector_calls"`
	Observations  []observation `json:"observations"`
}

type result struct {
	SchemaVersion    int               `json:"schema_version"`
	Mode             string            `json:"mode"`
	Module           string            `json:"module"`
	Version          string            `json:"version"`
	ModuleSum        string            `json:"module_sum"`
	ExecutableSHA256 string            `json:"executable_sha256"`
	ConfigSHA256     string            `json:"config_sha256"`
	RequestSHA256    string            `json:"request_sha256"`
	Bindings         map[string]string `json:"bindings"`
	Acquisitions     []acquisition     `json:"acquisitions"`
}

func digest(raw []byte) string {
	sum := sha256.Sum256(raw)
	return hex.EncodeToString(sum[:])
}

func validDigest(value string, size int) bool {
	decoded, err := hex.DecodeString(value)
	return err == nil && len(decoded) == size && value == strings.ToLower(value)
}

func provenance() (string, error) {
	info, ok := debug.ReadBuildInfo()
	if !ok {
		return "", errors.New("missing build provenance")
	}
	found := false
	for _, dep := range info.Deps {
		if dep.Path == modulePath {
			if dep.Version != moduleVersion || dep.Sum != moduleSum || dep.Replace != nil {
				return "", errors.New("pinned library provenance mismatch")
			}
			found = true
		}
	}
	if !found {
		return "", errors.New("missing pinned library")
	}
	executable, err := os.Executable()
	if err != nil {
		return "", errors.New("executable measurement failed")
	}
	raw, err := os.ReadFile(executable)
	if err != nil {
		return "", errors.New("executable measurement failed")
	}
	return digest(raw), nil
}

func openDirectory(absolute string) (int, error) {
	if !filepath.IsAbs(absolute) || filepath.Clean(absolute) != absolute {
		return -1, errors.New("absolute canonical source required")
	}
	fd, err := syscall.Open("/", syscall.O_RDONLY|syscall.O_DIRECTORY|syscall.O_NOFOLLOW, 0)
	if err != nil {
		return -1, err
	}
	for _, part := range strings.Split(strings.TrimPrefix(absolute, "/"), "/") {
		if part == "" {
			continue
		}
		next, openErr := syscall.Openat(fd, part, syscall.O_RDONLY|syscall.O_DIRECTORY|syscall.O_NOFOLLOW, 0)
		syscall.Close(fd)
		if openErr != nil {
			return -1, errors.New("unsafe source directory")
		}
		fd = next
	}
	return fd, nil
}

func safeRelative(relative string) bool {
	return relative != "." && relative != "" && !path.IsAbs(relative) &&
		path.Clean(relative) == relative && !strings.HasPrefix(relative, "../") &&
		!strings.ContainsAny(relative, "\\\x00")
}

func readFile(root int, relative string, size int64) ([]byte, error) {
	if !safeRelative(relative) || size < 0 || size > maxFile {
		return nil, errors.New("unsupported file selection")
	}
	fd, err := syscall.Dup(root)
	if err != nil {
		return nil, err
	}
	parts := strings.Split(relative, "/")
	for _, part := range parts[:len(parts)-1] {
		next, openErr := syscall.Openat(fd, part, syscall.O_RDONLY|syscall.O_DIRECTORY|syscall.O_NOFOLLOW, 0)
		syscall.Close(fd)
		if openErr != nil {
			return nil, errors.New("unsafe source ancestor")
		}
		fd = next
	}
	fileFD, err := syscall.Openat(fd, parts[len(parts)-1], syscall.O_RDONLY|syscall.O_NOFOLLOW|syscall.O_NONBLOCK, 0)
	syscall.Close(fd)
	if err != nil {
		return nil, errors.New("unsafe source file")
	}
	file := os.NewFile(uintptr(fileFD), "private-input")
	defer file.Close()
	var before, after syscall.Stat_t
	if syscall.Fstat(fileFD, &before) != nil || before.Mode&syscall.S_IFMT != syscall.S_IFREG ||
		before.Size != size || before.Nlink != 1 {
		return nil, errors.New("source file metadata mismatch")
	}
	raw, err := io.ReadAll(io.LimitReader(file, maxFile+1))
	if err != nil || len(raw) > maxFile || int64(len(raw)) != size ||
		syscall.Fstat(fileFD, &after) != nil || !stableFile(before, after) {
		return nil, errors.New("source changed during acquisition")
	}
	if !utf8.Valid(raw) || bytes.ContainsRune(raw, 0) ||
		bytes.Contains(bytes.ReplaceAll(raw, []byte("\r\n"), nil), []byte("\r")) {
		return nil, errors.New("unsupported source encoding")
	}
	return raw, nil
}

func stableFile(before, after syscall.Stat_t) bool {
	return before.Dev == after.Dev && before.Ino == after.Ino &&
		before.Mode == after.Mode && before.Size == after.Size &&
		before.Mtim == after.Mtim && before.Ctim == after.Ctim &&
		before.Nlink == after.Nlink && before.Uid == after.Uid && before.Gid == after.Gid
}

// Audit the selected tree independently; omitted regular files fail, never skip.
func selectedFiles(root int) ([]string, error) {
	var files []string
	entries := 0
	var walk func(int, string) error
	walk = func(fd int, prefix string) error {
		duplicate, err := syscall.Dup(fd)
		if err != nil {
			return err
		}
		directory := os.NewFile(uintptr(duplicate), "private-directory")
		children, err := directory.ReadDir(-1)
		directory.Close()
		if err != nil {
			return errors.New("source traversal failed")
		}
		for _, child := range children {
			entries++
			if entries > maxEntries {
				return errors.New("entry budget exceeded")
			}
			relative := child.Name()
			if prefix != "" {
				relative = prefix + "/" + relative
			}
			if !safeRelative(relative) {
				return errors.New("unsafe source name")
			}
			if child.Type()&os.ModeSymlink != 0 {
				continue // Internal links are recorded by the maintained producer, never followed.
			}
			if child.IsDir() {
				nested, err := syscall.Openat(fd, child.Name(), syscall.O_RDONLY|syscall.O_DIRECTORY|syscall.O_NOFOLLOW, 0)
				if err != nil {
					return errors.New("unsafe source traversal")
				}
				err = walk(nested, relative)
				syscall.Close(nested)
				if err != nil {
					return err
				}
			} else if child.Type().IsRegular() {
				files = append(files, relative)
				if len(files) > maxFiles {
					return errors.New("file budget exceeded")
				}
			} else {
				return errors.New("unsupported source type")
			}
		}
		return nil
	}
	if err := walk(root, ""); err != nil {
		return nil, err
	}
	sort.Strings(files)
	return files, nil
}

// v8.30.1 columns use the previous LF byte, not the next line's first byte.
// Match bytes are checked BEFORE redaction; no search or guessed offset is used.
func localize(raw []byte, origins []int, finding report.Finding, key []byte) (int, int, string, string) {
	if finding.StartLine < 1 || finding.StartColumn < 1 {
		return 0, 0, "", "unsupported_coordinates"
	}
	if finding.StartLine > len(origins) {
		return 0, 0, "", "unsupported_coordinates"
	}
	start := origins[finding.StartLine-1] + finding.StartColumn - 1
	end := start + len(finding.Match)
	if start < 0 || end <= start || end > len(raw) || !bytes.Equal(raw[start:end], []byte(finding.Match)) {
		return 0, 0, "", "unsupported_match_interval"
	}
	mac := hmac.New(sha256.New, key)
	mac.Write(raw[start:end])
	return start, end, hex.EncodeToString(mac.Sum(nil)), "mapped_acquired_full_file"
}

func scan(ctx context.Context, input request, rawRequest []byte, executable string) (result, error) {
	if input.SchemaVersion != 1 || len(input.Files) > maxFiles || !validDigest(input.Key, 32) ||
		len(input.Bindings) != 5 || !validDigest(input.Bindings["run_namespace"], 16) {
		return result{}, errors.New("invalid request")
	}
	for _, field := range []string{"source_sha256", "selection_sha256", "toolchain_sha256", "config_sha256"} {
		if !validDigest(input.Bindings[field], 32) {
			return result{}, errors.New("invalid binding")
		}
	}
	key, _ := hex.DecodeString(input.Key)
	detector, err := detect.NewDetectorDefaultConfig()
	if err != nil {
		return result{}, errors.New("embedded configuration failed")
	}
	detector.IgnoreGitleaksAllow = true
	detector.MaxDecodeDepth = 0
	detector.MaxArchiveDepth = 0
	detector.Redact = 0
	root, err := openDirectory(input.Source)
	if err != nil {
		return result{}, err
	}
	defer syscall.Close(root)
	selected, err := selectedFiles(root)
	if err != nil {
		return result{}, err
	}
	if len(selected) != len(input.Files) {
		return result{}, errors.New("incomplete file selection")
	}
	out := result{1, mode, modulePath, moduleVersion, moduleSum, executable,
		digest([]byte(config.DefaultConfig)), digest(rawRequest), input.Bindings, []acquisition{}}
	var total int64
	count := 0
	mappedBytes := 0
	for index, file := range input.Files {
		if ctx.Err() != nil {
			return result{}, errors.New("scan deadline exceeded")
		}
		total += file.Size
		if total > maxTree || file.Path != selected[index] || !validDigest(file.SHA256, 32) {
			return result{}, errors.New("invalid or oversized selection")
		}
		raw, err := readFile(root, file.Path, file.Size)
		if err != nil {
			return result{}, err
		}
		if digest(raw) != file.SHA256 {
			return result{}, errors.New("acquired file digest mismatch")
		}
		acquired := acquisition{file, 0, len(raw), 1, []observation{}}
		// The exact acquired string is the entire input to this one library call.
		findings := detector.DetectContext(ctx, detect.Fragment{Raw: string(raw), FilePath: file.Path, StartLine: 1})
		if ctx.Err() != nil {
			return result{}, errors.New("partial detector execution")
		}
		count += len(findings)
		if count > maxFindings {
			return result{}, errors.New("finding budget exceeded")
		}
		origins := []int{0}
		for index, value := range raw {
			if value == '\n' {
				origins = append(origins, index)
			}
		}
		for _, finding := range findings {
			mappedBytes += len(finding.Match)
			if mappedBytes > maxTree {
				return result{}, errors.New("mapping byte budget exceeded")
			}
			start, end, mac, status := localize(raw, origins, finding, key)
			finding.Fingerprint = fmt.Sprintf("%s:%s:%d", file.Path, finding.RuleID, finding.StartLine)
			finding.Redact(100)
			finding.Fragment = nil
			finding.Line = ""
			acquired.Observations = append(acquired.Observations, observation{finding, start, end, mac, status})
		}
		after, err := readFile(root, file.Path, file.Size)
		if err != nil || !bytes.Equal(raw, after) {
			return result{}, errors.New("source changed after detection")
		}
		out.Acquisitions = append(out.Acquisitions, acquired)
	}
	return out, nil
}

func unambiguous(raw []byte) bool {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	var value func(int) bool
	value = func(depth int) bool {
		if depth > 64 {
			return false
		}
		token, err := decoder.Token()
		if err != nil {
			return false
		}
		delimiter, composite := token.(json.Delim)
		if !composite {
			return true
		}
		switch delimiter {
		case '{':
			seen := map[string]bool{}
			for decoder.More() {
				key, err := decoder.Token()
				name, ok := key.(string)
				if err != nil || !ok || seen[name] {
					return false
				}
				seen[name] = true
				if !value(depth + 1) {
					return false
				}
			}
			end, err := decoder.Token()
			return err == nil && end == json.Delim('}')
		case '[':
			for decoder.More() {
				if !value(depth + 1) {
					return false
				}
			}
			end, err := decoder.Token()
			return err == nil && end == json.Delim(']')
		default:
			return false
		}
	}
	if !value(0) {
		return false
	}
	_, err := decoder.Token()
	return err == io.EOF
}

func main() {
	// Prevent upstream trace/debug logging from exposing input or findings.
	zerolog.SetGlobalLevel(zerolog.Disabled)
	if len(os.Args) == 2 && os.Args[1] == "identity" {
		executable, err := provenance()
		if err != nil {
			fail()
		}
		json.NewEncoder(os.Stdout).Encode(map[string]any{"mode": mode, "module": modulePath,
			"version": moduleVersion, "module_sum": moduleSum, "executable_sha256": executable,
			"config_sha256": digest([]byte(config.DefaultConfig))})
		return
	}
	if len(os.Args) != 1 {
		fail()
	}
	debug.SetMemoryLimit(512 * 1024 * 1024)
	if syscall.Setrlimit(syscall.RLIMIT_CPU, &syscall.Rlimit{Cur: 120, Max: 120}) != nil ||
		syscall.Setrlimit(syscall.RLIMIT_AS, &syscall.Rlimit{Cur: 4 * 1024 * 1024 * 1024, Max: 4 * 1024 * 1024 * 1024}) != nil {
		fail()
	}
	executable, err := provenance()
	if err != nil {
		fail()
	}
	raw, err := io.ReadAll(io.LimitReader(os.Stdin, maxDocument+1))
	if err != nil || len(raw) > maxDocument || !unambiguous(raw) {
		fail()
	}
	var input request
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	if decoder.Decode(&input) != nil || decoder.Decode(new(any)) != io.EOF {
		fail()
	}
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	defer cancel()
	out, err := scan(ctx, input, raw, executable)
	if err != nil {
		fail()
	}
	encoded, err := json.Marshal(out)
	if err != nil || len(encoded) > maxDocument {
		fail()
	}
	if _, err = os.Stdout.Write(encoded); err != nil {
		fail()
	}
}

func fail() {
	fmt.Fprintln(os.Stderr, "cdx adapter blocked")
	os.Exit(1)
}
