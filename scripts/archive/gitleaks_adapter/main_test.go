package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/rs/zerolog"
)

func privateTestDirectory(t *testing.T) string {
	t.Helper()
	suffix := make([]byte, 12)
	if _, err := rand.Read(suffix); err != nil {
		t.Fatal("random directory failed")
	}
	root, err := filepath.Abs(".test-" + hex.EncodeToString(suffix))
	if err != nil || os.Mkdir(root, 0700) != nil {
		t.Fatal("test directory failed")
	}
	t.Cleanup(func() { os.RemoveAll(root) })
	return root
}

func inputFor(t *testing.T, root string, raw []byte) request {
	t.Helper()
	if err := os.WriteFile(filepath.Join(root, "fixture.txt"), raw, 0600); err != nil {
		t.Fatal("fixture write failed")
	}
	return request{1, root, map[string]string{
		"run_namespace":    strings.Repeat("a", 32),
		"source_sha256":    strings.Repeat("b", 64),
		"selection_sha256": strings.Repeat("c", 64),
		"config_sha256":    strings.Repeat("d", 64),
		"toolchain_sha256": strings.Repeat("e", 64),
	}, strings.Repeat("f", 64), []fileInput{{"fixture.txt", digest(raw), int64(len(raw))}}}
}

func TestAcquiredLargeFullFile(t *testing.T) {
	zerolog.SetGlobalLevel(zerolog.Disabled)
	for _, newline := range []string{"\n", "\r\n"} {
		for _, size := range []int{99999, 100000, 100001, 200000} {
			root := privateTestDirectory(t)
			token := strings.Join([]string{"wE4r", "T6yU", "9iO2", "pA5s", "D8fG", "3hJ7", "kL0z"}, "")
			assignment := "api_key=\"" + token + "\"" + newline
			raw := []byte(strings.Repeat("x", size) + newline + "λ" + assignment + assignment)
			input := inputFor(t, root, raw)
			document, _ := json.Marshal(input)
			out, err := scan(context.Background(), input, document, "measured-test-tool")
			if err != nil {
				t.Fatal("synthetic full-file scan failed:", err)
			}
			acquired := out.Acquisitions[0]
			if acquired.OriginStart != 0 || acquired.OriginEnd != len(raw) || acquired.DetectorCalls != 1 ||
				len(acquired.Observations) < 2 {
				t.Fatal("incomplete acquisition or observations")
			}
			for _, observation := range acquired.Observations {
				if observation.MappingStatus != "mapped_acquired_full_file" || observation.Start < size ||
					observation.End > len(raw) || strings.Contains(observation.Record.Match, token) ||
					observation.Record.Secret != "REDACTED" {
					t.Fatal("unsafe or unmapped observation")
				}
			}
		}
	}
}

func TestAcquisitionRejectsDriftAndIncompleteSelection(t *testing.T) {
	root := privateTestDirectory(t)
	input := inputFor(t, root, []byte("safe fixture\n"))
	input.Files[0].SHA256 = strings.Repeat("0", 64)
	if _, err := scan(context.Background(), input, nil, "test"); err == nil {
		t.Fatal("accepted digest drift")
	}
	input = inputFor(t, root, []byte("safe fixture\n"))
	os.WriteFile(filepath.Join(root, "omitted.txt"), []byte("omitted"), 0600)
	if _, err := scan(context.Background(), input, nil, "test"); err == nil {
		t.Fatal("accepted omitted regular file")
	}
}

func TestAcquisitionRejectsUnsafeInputs(t *testing.T) {
	for _, raw := range [][]byte{{0}, {0xff}, []byte("bare\rnewline"), make([]byte, maxFile+1)} {
		root := privateTestDirectory(t)
		input := inputFor(t, root, raw)
		if _, err := scan(context.Background(), input, nil, "test"); err == nil {
			t.Fatal("accepted unsupported input")
		}
	}
	root := privateTestDirectory(t)
	input := inputFor(t, root, []byte("safe\n"))
	os.Rename(filepath.Join(root, "fixture.txt"), filepath.Join(root, "target.txt"))
	os.Symlink("target.txt", filepath.Join(root, "fixture.txt"))
	fd, err := openDirectory(root)
	if err != nil {
		t.Fatal("test root unavailable")
	}
	defer os.NewFile(uintptr(fd), "test-directory").Close()
	if _, err := readFile(fd, input.Files[0].Path, input.Files[0].Size); err == nil {
		t.Fatal("followed symlink")
	}
	if _, err := readFile(fd, "../escape", 1); err == nil {
		t.Fatal("accepted traversal")
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := scan(ctx, input, nil, "test"); err == nil {
		t.Fatal("accepted cancelled execution")
	}
}

func TestJSONAmbiguityRejected(t *testing.T) {
	for _, raw := range []string{`{"a":1,"a":2}`, `{"a":{"b":1,"b":2}}`, `{} {}`, `{"x":NaN}`} {
		if unambiguous([]byte(raw)) {
			t.Fatal("accepted ambiguous request")
		}
	}
	if !unambiguous([]byte(`{"a":[{"b":1}]}`)) {
		t.Fatal("rejected ordinary JSON")
	}
}
