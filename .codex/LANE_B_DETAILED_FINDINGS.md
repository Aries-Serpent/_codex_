# LANE B: Detailed CodeQL JavaScript Findings
**Total Findings:** 37
**Report Date:** 2026-07-13

---

## Findings by File

### site/assets/javascripts/lunr/tinyseg.js (5 findings)

#### Finding #37

**Location:** Line 110, Column 32

**Severity:** 🟠 WARNING

**Rule:** `js/unneeded-defensive-code`

**Rule Name:** N/A

**Message:** This guard always evaluates to false.

---

#### Finding #11

**Location:** Line 117, Column 16

**Severity:** 🟠 WARNING

**Rule:** `js/use-before-declaration`

**Rule Name:** N/A

**Message:** Variable 'i' is used before its [declaration](1).

---

#### Finding #6

**Location:** Line 119, Column 13

**Severity:** 🟠 WARNING

**Rule:** `js/automatic-semicolon-insertion`

**Rule Name:** N/A

**Message:** Avoid automated semicolon insertion (98% of all statements in [the enclosing function](1) have an explicit semicolon).

---

#### Finding #4

**Location:** Line 42, Column N/A

**Severity:** 🟠 WARNING

**Rule:** `js/automatic-semicolon-insertion`

**Rule Name:** N/A

**Message:** Avoid automated semicolon insertion (95% of all statements in [the enclosing function](1) have an explicit semicolon).

---

#### Finding #5

**Location:** Line 49, Column 11

**Severity:** 🟠 WARNING

**Rule:** `js/automatic-semicolon-insertion`

**Rule Name:** N/A

**Message:** Avoid automated semicolon insertion (95% of all statements in [the enclosing function](1) have an explicit semicolon).

---

### site/assets/javascripts/lunr/wordcut.js (32 findings)

#### Finding #12

**Location:** Line 1, Column 370

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable module.

---

#### Finding #13

**Location:** Line 1, Column 377

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable exports.

---

#### Finding #18

**Location:** Line 1123, Column 10

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused function identity.

---

#### Finding #7

**Location:** Line 1193, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/automatic-semicolon-insertion`

**Rule Name:** N/A

**Message:** Avoid automated semicolon insertion (97% of all statements in [the enclosing function](1) have an explicit semicolon).

---

#### Finding #35

**Location:** Line 1683, Column N/A

**Severity:** 🟠 WARNING

**Rule:** `js/useless-expression`

**Rule Name:** N/A

**Message:** This expression has no effect.

---

#### Finding #34

**Location:** Line 1778, Column 7

**Severity:** 🟠 WARNING

**Rule:** `js/useless-assignment-to-local`

**Rule Name:** N/A

**Message:** The initial value of abs is unused, since it is always overwritten.

---

#### Finding #19

**Location:** Line 1859, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable Minimatch.

---

#### Finding #20

**Location:** Line 1867, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable alphasort.

---

#### Finding #21

**Location:** Line 1868, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable alphasorti.

---

#### Finding #22

**Location:** Line 2231, Column 9

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable newPattern.

---

#### Finding #23

**Location:** Line 2332, Column 7

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable self.

---

#### Finding #1

**Location:** Line 2505, Column 9

**Severity:** 🟠 WARNING

**Rule:** `js/trivial-conditional`

**Rule Name:** N/A

**Message:** This use of variable 'needDir' always evaluates to true.

---

#### Finding #24

**Location:** Line 2512, Column 7

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable exists.

---

#### Finding #25

**Location:** Line 2576, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable Minimatch.

---

#### Finding #26

**Location:** Line 2577, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable Glob.

---

#### Finding #27

**Location:** Line 2578, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable util.

---

#### Finding #28

**Location:** Line 2583, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable alphasort.

---

#### Finding #29

**Location:** Line 2584, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable alphasorti.

---

#### Finding #30

**Location:** Line 2781, Column 7

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable abs.

---

#### Finding #31

**Location:** Line 2808, Column 7

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable stat.

---

#### Finding #32

**Location:** Line 2830, Column 7

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable entries.

---

#### Finding #2

**Location:** Line 2985, Column 9

**Severity:** 🟠 WARNING

**Rule:** `js/trivial-conditional`

**Rule Name:** N/A

**Message:** This use of variable 'needDir' always evaluates to true.

---

#### Finding #33

**Location:** Line 2992, Column 7

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable exists.

---

#### Finding #15

**Location:** Line 308, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable WordcutCore.

---

#### Finding #16

**Location:** Line 323, Column 9

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable self.

---

#### Finding #3

**Location:** Line 3573, Column 13

**Severity:** 🟠 WARNING

**Rule:** `js/trivial-conditional`

**Rule Name:** N/A

**Message:** This use of variable 'inClass' always evaluates to true.

---

#### Finding #36

**Location:** Line 4130, Column 18

**Severity:** 🟠 WARNING

**Rule:** `js/useless-expression`

**Rule Name:** N/A

**Message:** This expression has no effect.

---

#### Finding #8

**Location:** Line 4374, Column N/A

**Severity:** 🟠 WARNING

**Rule:** `js/automatic-semicolon-insertion`

**Rule Name:** N/A

**Message:** Avoid automated semicolon insertion (93% of all statements in [the enclosing function](1) have an explicit semicolon).

---

#### Finding #9

**Location:** Line 4511, Column N/A

**Severity:** 🟠 WARNING

**Rule:** `js/automatic-semicolon-insertion`

**Rule Name:** N/A

**Message:** Avoid automated semicolon insertion (93% of all statements in [the enclosing function](1) have an explicit semicolon).

---

#### Finding #17

**Location:** Line 489, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable sys.

---

#### Finding #10

**Location:** Line 5915, Column 21

**Severity:** 🟠 WARNING

**Rule:** `js/regex/unmatchable-caret`

**Rule Name:** N/A

**Message:** This assertion can never match.

---

#### Finding #14

**Location:** Line 64, Column 5

**Severity:** 🟠 WARNING

**Rule:** `js/unused-local-variable`

**Rule Name:** N/A

**Message:** Unused variable glob.

---


---

## Finding Summary Table

| # | File | Line | Col | Rule | Message (truncated) |
|---|------|------|-----|------|---------------------|
| 1 | `wordcut.js` | 2505 | 9 | `js/trivial-conditional` | This use of variable 'needDir' always evaluates to... |
| 2 | `wordcut.js` | 2985 | 9 | `js/trivial-conditional` | This use of variable 'needDir' always evaluates to... |
| 3 | `wordcut.js` | 3573 | 13 | `js/trivial-conditional` | This use of variable 'inClass' always evaluates to... |
| 4 | `tinyseg.js` | 42 | N/A | `js/automatic-semicolon-insertion` | Avoid automated semicolon insertion (95% of all st... |
| 5 | `tinyseg.js` | 49 | 11 | `js/automatic-semicolon-insertion` | Avoid automated semicolon insertion (95% of all st... |
| 6 | `tinyseg.js` | 119 | 13 | `js/automatic-semicolon-insertion` | Avoid automated semicolon insertion (98% of all st... |
| 7 | `wordcut.js` | 1193 | 5 | `js/automatic-semicolon-insertion` | Avoid automated semicolon insertion (97% of all st... |
| 8 | `wordcut.js` | 4374 | N/A | `js/automatic-semicolon-insertion` | Avoid automated semicolon insertion (93% of all st... |
| 9 | `wordcut.js` | 4511 | N/A | `js/automatic-semicolon-insertion` | Avoid automated semicolon insertion (93% of all st... |
| 10 | `wordcut.js` | 5915 | 21 | `js/regex/unmatchable-caret` | This assertion can never match. |
| 11 | `tinyseg.js` | 117 | 16 | `js/use-before-declaration` | Variable 'i' is used before its [declaration](1). |
| 12 | `wordcut.js` | 1 | 370 | `js/unused-local-variable` | Unused variable module. |
| 13 | `wordcut.js` | 1 | 377 | `js/unused-local-variable` | Unused variable exports. |
| 14 | `wordcut.js` | 64 | 5 | `js/unused-local-variable` | Unused variable glob. |
| 15 | `wordcut.js` | 308 | 5 | `js/unused-local-variable` | Unused variable WordcutCore. |
| 16 | `wordcut.js` | 323 | 9 | `js/unused-local-variable` | Unused variable self. |
| 17 | `wordcut.js` | 489 | 5 | `js/unused-local-variable` | Unused variable sys. |
| 18 | `wordcut.js` | 1123 | 10 | `js/unused-local-variable` | Unused function identity. |
| 19 | `wordcut.js` | 1859 | 5 | `js/unused-local-variable` | Unused variable Minimatch. |
| 20 | `wordcut.js` | 1867 | 5 | `js/unused-local-variable` | Unused variable alphasort. |
| 21 | `wordcut.js` | 1868 | 5 | `js/unused-local-variable` | Unused variable alphasorti. |
| 22 | `wordcut.js` | 2231 | 9 | `js/unused-local-variable` | Unused variable newPattern. |
| 23 | `wordcut.js` | 2332 | 7 | `js/unused-local-variable` | Unused variable self. |
| 24 | `wordcut.js` | 2512 | 7 | `js/unused-local-variable` | Unused variable exists. |
| 25 | `wordcut.js` | 2576 | 5 | `js/unused-local-variable` | Unused variable Minimatch. |
| 26 | `wordcut.js` | 2577 | 5 | `js/unused-local-variable` | Unused variable Glob. |
| 27 | `wordcut.js` | 2578 | 5 | `js/unused-local-variable` | Unused variable util. |
| 28 | `wordcut.js` | 2583 | 5 | `js/unused-local-variable` | Unused variable alphasort. |
| 29 | `wordcut.js` | 2584 | 5 | `js/unused-local-variable` | Unused variable alphasorti. |
| 30 | `wordcut.js` | 2781 | 7 | `js/unused-local-variable` | Unused variable abs. |
| 31 | `wordcut.js` | 2808 | 7 | `js/unused-local-variable` | Unused variable stat. |
| 32 | `wordcut.js` | 2830 | 7 | `js/unused-local-variable` | Unused variable entries. |
| 33 | `wordcut.js` | 2992 | 7 | `js/unused-local-variable` | Unused variable exists. |
| 34 | `wordcut.js` | 1778 | 7 | `js/useless-assignment-to-local` | The initial value of abs is unused, since it is al... |
| 35 | `wordcut.js` | 1683 | N/A | `js/useless-expression` | This expression has no effect. |
| 36 | `wordcut.js` | 4130 | 18 | `js/useless-expression` | This expression has no effect. |
| 37 | `tinyseg.js` | 110 | 32 | `js/unneeded-defensive-code` | This guard always evaluates to false. |
