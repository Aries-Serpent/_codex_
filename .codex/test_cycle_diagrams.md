# Phase 5 Test-Cycle Healing Diagrams

Generated test healing cycles for flaky test fixes.

## 1. 1__coverage_phase5_lane_002

```mermaid
graph TD
    A["🟡 @pytest.mark.flaky<br/>coverage_phase5_lane_002"] --> B["Detect<br/>reruns=3"]
    B --> C["Diagnose<br/>Root cause analysis"]
    C --> D{Root Cause?}
    D -->|Network| E["Action<br/>Keep reruns=2, add reason"]
    D -->|Race condition| F["Action<br/>Fix timing, remove flaky"]
    D -->|P19 shadow| G["Action<br/>Apply P19 fix first"]
    D -->|Non-deterministic| H["Action<br/>Seed RNG, remove flaky"]
    E --> I["✅ Tuned<br/>Flaky marker optimized"]
    F --> J["✅ Fixed<br/>Root cause addressed"]
    G --> J
    H --> J

    style A fill:#ffd93d
    style I fill:#51cf66
    style J fill:#51cf66
```

## 2. 2__coverage_phase5_lane_004

```mermaid
graph TD
    A["🟣 Naive DateTime<br/>coverage_phase5_lane_004"] --> B["Detect<br/>datetime.now() no tz"]
    B --> C["Diagnose<br/>Timezone-unaware comparison"]
    C --> D["Fix<br/>Use timezone.utc"]
    D --> E["Verify<br/>Across timezones"]
    E --> F{Portable?}
    F -->|Yes| G["✅ Fixed<br/>TZ-aware datetime"]
    F -->|No| H["Debug<br/>Check comparisons"]
    H --> C

    style A fill:#a78bfa
    style G fill:#51cf66
    style H fill:#ffd43b
```

## 3. 3__coverage_phase5_lane_005

```mermaid
graph TD
    A["⚫ Platform Path<br/>coverage_phase5_lane_005"] --> B["Detect<br/>os.path.* operations"]
    B --> C["Diagnose<br/>Platform-specific failures"]
    C --> D["Fix<br/>Use pathlib.Path"]
    D --> E["Test<br/>Windows/Linux/macOS"]
    E --> F{All Platforms Pass?}
    F -->|Yes| G["✅ Abstract<br/>Cross-platform paths"]
    F -->|No| H["Investigate<br/>Path separator issues"]
    H --> C

    style A fill:#333333,color:#fff
    style G fill:#51cf66
    style H fill:#ffd43b
```
