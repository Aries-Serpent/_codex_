# Cognitive App Troubleshooting Guide
**Version:** v0.2.0  
**Last Updated:** 2026-07-17

---

## Common Issues & Solutions

### Installation & Setup

#### Issue: "npm ERR! ERESOLVE unable to resolve dependency tree"

**Cause:** Conflicting package versions  
**Solution:**
```bash
# Use npm legacy peer deps flag
npm install --legacy-peer-deps

# Or clean install
rm -rf node_modules package-lock.json
npm install
```

---

#### Issue: "Cannot find module '@/components/...'"

**Cause:** Path alias not configured  
**Solution:**
```typescript
// Check vite.config.ts contains:
resolve: {
  alias: {
    '@': resolve(projectRoot, 'src')
  }
}

// If still failing, restart dev server:
npm run dev
```

---

#### Issue: TypeScript errors in IDE but app runs fine

**Cause:** TypeScript version mismatch  
**Solution:**
```bash
# Update TypeScript
npm install --save-dev typescript@latest

# Rebuild
npm run dev

# In VS Code: Cmd+Shift+P → TypeScript: Select Version → Use Workspace
```

---

### Development Server

#### Issue: "Port 5173 already in use"

**Cause:** Another process using the port  
**Solution:**

```bash
# Kill process on port 5173
# macOS/Linux:
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or use different port:
npm run dev -- --port 3000
```

---

#### Issue: "EADDRINUSE: address already in use"

**Cause:** Port binding failed  
**Solution:**
```bash
# Try different port
npm run dev -- --port 3001

# Or kill node processes
pkill -f "node.*vite"
npm run dev
```

---

#### Issue: Hot module replacement (HMR) not working

**Cause:** Vite HMR misconfigured  
**Solution:**
```javascript
// In vite.config.ts:
export default defineConfig({
  server: {
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5173
    }
  }
});
```

---

### Runtime Errors

#### Issue: "Cannot read property 'state' of undefined" in console

**Cause:** Hook returning undefined during loading  
**Solution:**
```typescript
// Check components properly handle loading state:
if (loading && !state) {
  return <LoadingSpinner />;
}

if (error) {
  return <ErrorAlert error={error} />;
}

if (!state) return null;

// Now safe to access state properties
```

---

#### Issue: "Uncaught TypeError: Cannot read properties of null"

**Cause:** Component mounted before data fetched  
**Solution:**
```typescript
// Add proper null checks
const { state } = useQuantumState(true, 10000);

// Instead of: state.k1_factor
// Use: state?.k1_factor
return <div>{state?.k1_factor ?? 'Loading...'}</div>;
```

---

#### Issue: Console shows "404 error for /api/quantum/state"

**Cause:** Backend API not available (expected in development)  
**Solution:**
```typescript
// This is NORMAL - app uses mock data
// Check browser console for warnings (not errors)
// Mock data automatically provides fallback values

// To enable actual API calls in production:
// 1. Implement FastAPI backend (v0.3.0)
// 2. Set VITE_API_URL environment variable
// 3. Update API client in src/components/...
```

---

### Build & Production

#### Issue: "npm run build" fails with "ERR! premature close"

**Cause:** Memory limit exceeded  
**Solution:**
```bash
# Increase Node memory limit
NODE_OPTIONS="--max-old-space-size=4096" npm run build

# Or increase in package.json:
"build": "NODE_OPTIONS=--max-old-space-size=4096 tsc -b --noCheck && vite build"
```

---

#### Issue: Build succeeds but missing assets in dist/

**Cause:** Vite build misconfiguration  
**Solution:**
```typescript
// Check vite.config.ts:
build: {
  outDir: 'dist',
  emptyOutDir: true,
  rollupOptions: {
    output: {
      manualChunks: {
        'vendor': ['react', 'react-dom']
      }
    }
  }
}

// Rebuild
npm run build
```

---

#### Issue: "Error: Cannot find module 'vite'" during build

**Cause:** Vite not installed  
**Solution:**
```bash
npm install --save-dev vite@latest
npm run build
```

---

### Deployment

#### Issue: App deployed but shows blank page or 404

**Cause:** Base path misconfigured  
**Solution:**
```typescript
// In vite.config.ts, verify:
base: process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/'

// For GitHub Pages deployment:
// URL should be: https://aries-serpent.github.io/_codex_/cognitive_app/
// NOT: https://aries-serpent.github.io/cognitive_app/
```

---

#### Issue: "Failed to load module script" after deployment

**Cause:** MIME type issues with GitHub Pages  
**Solution:**
```yaml
# Add to .gitattributes
*.js   text eol=lf
*.ts   text eol=lf
*.tsx  text eol=lf
*.css  text eol=lf
*.html text eol=lf
```

---

#### Issue: Deployment workflow fails with "Error: Process completed with exit code 128"

**Cause:** Git authentication issue  
**Solution:**
```yaml
# Check .github/workflows/deploy-cognitive-app.yml:
- name: Deploy to GitHub Pages
  uses: actions/deploy-pages@v2
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    # For private repos, use:
    # token: ${{ secrets.CODEX_MASTER_KEY }}
```

---

### Features Not Working

#### Issue: Dashboard tab shows "No data available"

**Cause:** Mock API not loaded  
**Solution:**
```typescript
// Check src/hooks/use-quantum-state.ts:
- Verify mock data is imported
- Ensure setInterval is working
- Check browser DevTools → Network tab for failed requests

// Expected: Mock data updates every 10 seconds
// Check: DevTools Console → look for "Fetching quantum state..."
```

---

#### Issue: Memory search returns no results

**Cause:** Pattern library not populated  
**Solution:**
```typescript
// Check src/hooks/use-memory-system.ts:
// Verify INITIAL_PATTERNS has data
// Try searching for common terms: "pattern", "memory", "deploy"

// If still failing:
// 1. Check browser localStorage isn't full
// 2. Clear cache: Cmd+Shift+Delete → All time
// 3. Reload app and retry
```

---

#### Issue: Code generation not working

**Cause:** Mock API client error  
**Solution:**
```typescript
// Check src/components/code/CodeGenerator.tsx:
// 1. Verify prompt is entered
// 2. Check language dropdown has a selection
// 3. Open DevTools Console → verify no errors
// 4. Try simplified prompt: "function add(a, b) { return a + b; }"
```

---

#### Issue: Quantum visualizer not animating

**Cause:** CSS animations disabled  
**Solution:**
```css
/* Check tailwind.config.js has animation config */
animation: {
  'spin': 'spin 1s linear infinite',
  // ... other animations
}

/* Verify prefers-reduced-motion not set in OS */
// Windows: Settings → Ease of Access → Display → Show animations
// macOS: System Preferences → Accessibility → Display → Reduce motion
```

---

#### Issue: Terminal (CLI tab) not responding

**Cause:** xterm.js not initialized  
**Solution:**
```typescript
// In src/components/cli/XtermTerminal.tsx:
// 1. Verify DOM element with id="terminal" exists
// 2. Check FitAddon is loaded
// 3. Verify terminal.open(element) is called

// Try refreshing page
// If still failing, check browser console for xterm errors
```

---

### Performance Issues

#### Issue: App slow to load on first visit

**Cause:** Large bundle size  
**Solution:**
```typescript
// Enable code splitting in vite.config.ts:
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'react': ['react', 'react-dom'],
        'ui': ['@radix-ui/*'],
        'charts': ['recharts']
      }
    }
  }
}

// Rebuild:
npm run build

// Check bundle size:
npm install -g bundlesize
bundlesize
```

---

#### Issue: Dashboard metrics update slowly

**Cause:** Refresh interval too long  
**Solution:**
```typescript
// In App.tsx:
// Change interval from 10000ms to 5000ms:
<QuantumDecisionEngine />

// Or configure globally:
const REFRESH_INTERVAL = 5000; // 5 seconds
```

---

#### Issue: Memory search slow with large datasets

**Cause:** Unoptimized search algorithm  
**Solution:**
```typescript
// Use debouncing in search input:
const handleSearch = useMemo(
  () => debounce((query: string) => searchMemories(query), 300),
  [searchMemories]
);

// Or limit search to first 1000 patterns:
searchMemories(query, { limit: 1000 })
```

---

### Accessibility Issues

#### Issue: Tab navigation skipping elements

**Cause:** Missing tabindex or role attributes  
**Solution:**
```typescript
// Add to interactive elements:
<button
  type="button"
  role="button"
  tabIndex={0}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  Click me
</button>
```

---

#### Issue: Screen reader not announcing changes

**Cause:** Missing ARIA live regions  
**Solution:**
```typescript
// Add live regions for updates:
<div role="status" aria-live="polite" aria-atomic="true">
  {message}
</div>

// Use aria-label for icon buttons:
<button aria-label="Close dialog">✕</button>
```

---

### Dark Mode Issues

#### Issue: Dark mode toggle not working

**Cause:** Theme provider not initialized  
**Solution:**
```typescript
// Check App.tsx for theme context:
<ThemeProvider attribute="class" defaultTheme="system">
  {children}
</ThemeProvider>

// Verify tailwind.config.js has dark mode:
darkMode: 'class'

// Clear browser cache and reload
```

---

#### Issue: Colors look wrong in dark mode

**Cause:** OKLCH values need adjustment  
**Solution:**
```css
/* Use CSS variables with dark: prefix */
.card {
  @apply bg-card dark:bg-slate-900;
}

/* Or adjust OKLCH colors */
@media (prefers-color-scheme: dark) {
  :root {
    --background: oklch(0.15 0.02 280);
    --foreground: oklch(0.95 0.02 280);
  }
}
```

---

### Browser-Specific Issues

#### Issue: App doesn't work in Safari

**Cause:** Missing polyfills or unsupported features  
**Solution:**
```typescript
// Check for modern JS usage:
// Replace: Array.at() → arr[arr.length - 1]
// Replace: Promise.all() compat is OK
// Verify: no top-level await

// Add to package.json:
"browserslist": ["last 2 versions", "> 1%"]

// Rebuild: npm run build
```

---

#### Issue: Console warns about "Unexpected token <"

**Cause:** MIME type issue with module imports  
**Solution:**
```yaml
# Add .gitattributes:
*.js   text eol=lf
*.ts   text eol=lf
*.tsx  text eol=lf
*.jsx  text eol=lf

# Verify vite.config.ts has correct entry:
server: {
  middlewareMode: true,
  headers: {
    'Content-Type': 'application/javascript'
  }
}
```

---

#### Issue: Firefox shows "XHR failed loading"

**Cause:** CORS policy or network error  
**Solution:**
```typescript
// Mock API should work without CORS
// If calling real API, add CORS headers:
headers: {
  'Access-Control-Allow-Origin': '*'
}

// Or proxy API through same domain in production
```

---

## Debug Mode

### Enable Debug Logging

```typescript
// In src/main.tsx:
if (import.meta.env.DEV) {
  window.__DEBUG__ = true;
}

// In components:
if (window.__DEBUG__) {
  console.log('Debug info:', state);
}
```

### Browser DevTools Tips

```javascript
// React DevTools
// 1. Install React Developer Tools extension
// 2. Open DevTools → Components tab
// 3. Inspect component props and state

// Network tab
// 1. Open DevTools → Network tab
// 2. Look for API requests
// 3. Check response payloads

// Console
// 1. Filter by errors
// 2. Check for deprecation warnings
// 3. Look for custom debug logs
```

---

## Getting Help

### Before reporting issues:

1. **Check this guide** - Most issues have solutions here
2. **Search GitHub Issues** - Similar issue might exist
3. **Check browser console** - Copy full error message
4. **Try clearing cache** - Cmd+Shift+Delete (Chrome)
5. **Verify dependencies** - `npm list` shows all packages

### When reporting issues:

Include:
- Node.js version: `node --version`
- npm version: `npm --version`
- Browser: `Chrome 120.0.0`
- Full error message from console
- Steps to reproduce
- Screenshots if visual issue

### Useful commands for debugging:

```bash
# Check versions
node --version
npm --version

# List installed packages
npm list

# Check for security vulnerabilities
npm audit

# Run tests to catch issues early
npm test

# Build with verbose output
npm run build -- --reportCompressedSize=false

# Check bundle contents
npm install -g vite-bundle-visualizer
vite-bundle-visualizer
```

---

## Performance Checklist

- [ ] App loads in < 3 seconds
- [ ] Tabs switch instantly (< 100ms)
- [ ] Search completes in < 500ms
- [ ] Dashboard updates smoothly
- [ ] No console errors or warnings
- [ ] Memory stable over time (no leaks)
- [ ] Mobile performs well (< 60fps)

---

## Security Checklist

- [ ] No hardcoded API keys
- [ ] XSS protection (sanitize user input)
- [ ] CSRF tokens for mutations (when backend added)
- [ ] Environment variables for sensitive data
- [ ] Dependencies up-to-date (`npm audit`)
- [ ] No console.log() of sensitive data
- [ ] Secrets not committed to git

---

*Last Updated: 2026-07-17 | Maintained by: Copilot CLI*
