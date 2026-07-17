# Cognitive App Quick-Start Guide
**Version:** v0.2.0  
**Last Updated:** 2026-07-17

---

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Node.js 22+ ([download](https://nodejs.org/))
- npm 10+ (included with Node.js)
- Git
- Terminal/Command Prompt

---

## 1. Clone & Install

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_/cognitive_app

# Install dependencies
npm install

# Verify installation
npm list | head -20
```

**Expected output:** Dependency tree with 60+ packages.

---

## 2. Start Development Server

```bash
# Run development server
npm run dev

# Expected output:
#   VITE v7.3.6 ready in XXX ms
#   ➜  Local:   http://localhost:5173/
#   ➜  Press h + enter to show help
```

Open **http://localhost:5173/** in your browser.

---

## 3. Explore the Features

### Dashboard Tab
- Real-time metrics visualization
- Quantum advantage metrics (2.86×)
- k₁ factor tracking
- Auto-refresh every 10 seconds

### Code Tab
- Natural language to code generation
- Monaco editor with syntax highlighting
- Multi-language support (Python, TypeScript, Go, etc.)
- Copy/download code

### Demo Tab
- Execute generated code
- Resource monitoring
- Console output capture

### Quantum Tab
- Quantum state visualization
- Wave function collapse animation
- Superposition state cards
- Decision tree exploration

### Memory Tab
- STM/LTM memory system
- Pattern library search
- Consolidation triggers
- Cache statistics

### Agents Tab
- Agent orchestration panel
- 6 physics paradigms
- Pre-built workflow tokens
- Custom token creation wizard

### Physics Tab
- Quantum decision engine metrics
- Coherence monitoring
- Phase progression
- Real-time decision tracking

### CLI Tab
- Terminal emulation (xterm)
- API client tester
- Command execution

### Docs Tab
- Comprehensive documentation
- Searchable content
- Mermaid diagrams
- Code examples

---

## 4. Build for Production

```bash
# Build optimized production bundle
npm run build

# Output directory: dist/
# Expected: index.html, assets/*.js, assets/*.css

# Preview production build locally
npm run preview

# Open http://localhost:4173/
```

---

## 5. Deploy to GitHub Pages

The app automatically deploys when you push to `main`:

```bash
# Push changes to main branch
git add .
git commit -m "Update cognitive app"
git push origin main

# Monitor deployment:
# https://github.com/Aries-Serpent/_codex_/actions

# View live app:
# https://aries-serpent.github.io/_codex_/cognitive_app/
```

---

## 📚 Project Structure

```
cognitive_app/
├── src/
│   ├── components/
│   │   ├── quantum/          # 27 quantum components
│   │   ├── code/             # 4 code generation components
│   │   ├── cli/              # Terminal & API client
│   │   ├── documentation/    # Doc viewer & search
│   │   ├── ui/               # 44 shadcn/ui components
│   │   └── __tests__/        # Component tests
│   ├── hooks/                # Custom React hooks
│   ├── lib/                  # Utilities & helpers
│   ├── App.tsx               # Main app component
│   ├── main.tsx              # Entry point
│   └── styles/               # Global styles
├── public/                   # Static assets
├── dist/                     # Built output (after build)
├── package.json              # Dependencies & scripts
├── tsconfig.json             # TypeScript config
├── vite.config.ts            # Vite config
└── README.md                 # Full documentation
```

---

## 🔧 Development Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start dev server (http://localhost:5173) |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |
| `npm run test` | Run unit tests |
| `npm run test:watch` | Watch mode for tests |
| `npm run test:ui` | Vitest UI dashboard |
| `npm run test:coverage` | Generate coverage report |
| `npm run test:e2e` | Run Playwright tests |
| `npm run test:e2e:ui` | Playwright UI mode |
| `npm run optimize` | Vite dependency optimization |

---

## 🌍 Environment Variables

### Development
```bash
# .env.development (optional)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

### Production
```bash
# .env.production
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://api.example.com/ws
```

### Current Status
- **Backend:** Mock API (uses fallback data)
- **Next Step:** Implement FastAPI backend in v0.3.0

---

## 🐛 Troubleshooting

### Issue: "Cannot find module @/components/..."
**Solution:** Verify path alias in `vite.config.ts`:
```typescript
resolve: {
  alias: {
    '@': resolve(projectRoot, 'src')
  }
}
```

### Issue: "Port 5173 already in use"
**Solution:** Use a different port:
```bash
npm run dev -- --port 3000
```

Or kill the existing process:
```bash
# macOS/Linux
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Issue: "Module not found" errors after npm install
**Solution:** Clear cache and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: App loads but no data in dashboard
**Solution:** Mock API is active. Check browser console:
- Open DevTools (F12)
- Check Console tab for errors
- Verify hooks are fetching mock data
- Data should auto-refresh every 10 seconds

### Issue: TypeScript errors in IDE
**Solution:** Ensure TypeScript 5.7.2+ is installed:
```bash
npm list typescript
npm install --save-dev typescript@latest
```

---

## 📖 Documentation References

| Document | Purpose | Location |
|----------|---------|----------|
| **Full Documentation** | Feature overview, architecture | `/docs/cognitive_app.md` |
| **Integration Guide** | API integration, backend setup | `README_INTEGRATION.md` |
| **Master Plan** | Backend specification, workflows | `CODEX_INTEGRATION_MASTER_PLAN.md` |
| **Implementation Status** | Progress tracking, known gaps | `IMPLEMENTATION_STATUS.md` |
| **Component Library** | Component API reference | `src/components/quantum/README.md` |
| **This Guide** | Quick start & troubleshooting | `.codex/reports/QUICK_START_GUIDE.md` |

---

## 🎓 Learning Resources

### Understanding the Components

#### Quantum Decision Engine
- Tracks quantum advantage metrics
- Visualizes decision making process
- Shows superposition states (parallel scenarios)
- Monitors coherence and k₁ factor

```typescript
import { QuantumDecisionEngine } from '@/components/quantum/QuantumDecisionEngine';

// In your component:
<QuantumDecisionEngine />
```

#### Memory Management Dashboard
- Manages STM (Short-Term Memory) and LTM (Long-Term Memory)
- Search across patterns with full-text search
- Consolidate memories when STM reaches 80%
- View compression statistics

```typescript
import { MemoryManagementDashboard } from '@/components/quantum/MemoryManagementDashboard';

// In your component:
<MemoryManagementDashboard />
```

#### Code Generator
- Generate code from natural language prompts
- Multi-language support
- Real-time complexity metrics
- Copy/download code

```typescript
import { CodeGenerator } from '@/components/code/CodeGenerator';

// In your component:
<CodeGenerator />
```

### Custom Hooks

#### useQuantumState
```typescript
const { state, loading, error } = useQuantumState(
  enabled: boolean,
  interval: number
);
```

#### useMemorySystem
```typescript
const { 
  state, 
  searchResults, 
  searching,
  searchMemories,
  consolidateMemory 
} = useMemorySystem(
  enabled: boolean,
  interval: number
);
```

---

## 🚢 Production Deployment Checklist

Before deploying to production:

- [ ] Build passes without errors: `npm run build`
- [ ] No console errors in browser DevTools
- [ ] All tabs are functional
- [ ] Responsive design tested on mobile/tablet/desktop
- [ ] Keyboard navigation working
- [ ] Dark/light mode toggle functional
- [ ] API endpoints ready (or mock fallback verified)
- [ ] Environment variables configured
- [ ] Performance is acceptable (<3s page load)
- [ ] Accessibility check passed (WCAG 2.1 AA)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and test locally
4. Commit with clear messages: `git commit -m "feat: add new feature"`
5. Push to your fork: `git push origin feature/my-feature`
6. Open a Pull Request

---

## ❓ FAQ

**Q: Can I use this offline?**  
A: Yes! Once built and deployed to GitHub Pages, the app works offline (except API calls). Mock data is used during development.

**Q: How do I contribute new components?**  
A: Add components to `src/components/`, follow existing patterns (TypeScript, styled with Tailwind), and add tests in `__tests__/`.

**Q: Can I customize the theme?**  
A: Yes! Edit `tailwind.config.js` and `src/styles/` files. The app uses OKLCH color system for accessibility.

**Q: How do I add a new tab?**  
A: Add a new `TabsTrigger` and `TabsContent` in `App.tsx`, then import your component.

**Q: What's the backend API?**  
A: Currently using mock data. Backend will be implemented in v0.3.0 using FastAPI.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions)
- **Documentation:** [Cognitive App Docs](https://aries-serpent.github.io/_codex_/cognitive_app/)

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

*Last Updated: 2026-07-17 | Maintained by: Copilot CLI*
