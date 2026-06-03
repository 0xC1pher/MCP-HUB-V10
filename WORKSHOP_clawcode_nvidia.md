# WORKSHOP: claw-code NVIDIA NIM Support
**Status:** PLANNED (not started)
**Priority:** HIGH
**Date:** 2026-06-03

---

## Problem Statement

claw-code enforces a strict `provider/model` format (exactly ONE slash) for model identification. NVIDIA NIM uses `org/model` format (organization/model). When combined with the `openai/` prefix routing, this creates `openai/org/model` (TWO slashes), which claw-code rejects as invalid syntax.

**Examples:**
| Input | Parsed As | Result |
|-------|-----------|--------|
| `openai/gpt-oss-20b` | provider=`openai`, model=`gpt-oss-20b` | ✅ VALID |
| `openai/deepseek-ai/deepseek-v4-flash` | provider=`openai`, model=`deepseek-ai/deepseek-v4-flash` | ❌ INVALID (extra slash) |
| `openai/meta/llama-3.3-70b-instruct` | provider=`openai`, model=`meta/llama-3.3-70b-instruct` | ❌ INVALID (extra slash) |

---

## Why This Happens: Architecture Reference

### 1. Model Resolution Flow (claw-code binary)

```
User Input: --model "openai/deepseek-v4-flash"
         │
         ▼
┌─────────────────────────────┐
│ parse_model_with_provider() │ ← crates/api/src/providers/openai_compat.rs
│                             │
│ 1. Split on FIRST '/'       │
│ 2. provider = "openai"      │
│ 3. model = "deepseek-v4..." │
│ 4. VALIDATE: model must not │
│    contain '/'              │ ← HERE IS THE REJECTION
│ 5. Return error             │
└─────────────────────────────┘
```

**Source code reference (from binary analysis):**
```rust
// crates/api/src/providers/openai_compat.rs (approximate)
fn parse_model_with_provider(model: &str) -> Result<ProviderMetadata, Error> {
    let parts: Vec<&str> = model.splitn(2, '/').collect();
    if parts.len() != 2 {
        return Err("invalid_model_syntax");
    }
    let provider_prefix = parts[0];
    let model_id = parts[1];
    
    // VALIDATION: model_id must not contain('/')
    if model_id.contains('/') {
        return Err("invalid_model_syntax: Expected provider/model");
    }
    // ... resolve provider metadata
}
```

### 2. Provider Detection Flow

```
Model String
    │
    ▼
┌──────────────────────────────────┐
│ Provider Detection (mod.rs)      │
│                                  │
│ if starts_with("claude") → Anthropic
│ if starts_with("grok") → xAI    │
│ if starts_with("openai/") → OpenAI
│ if starts_with("gpt-") → OpenAI │
│ if starts_with("qwen/") → DashScope
│ if starts_with("kimi/") → DashScope
│                                  │
│ *** NO NVIDIA DETECTION ***      │
└──────────────────────────────────┘
```

**Why no NVIDIA?** claw-code was designed for:
- Anthropic (Claude models)
- OpenAI (GPT models)
- xAI (Grok models)
- DashScope (Qwen, Kimi models)

NVIDIA NIM wasn't in the original provider list.

### 3. OpenAI-Compatible Provider Flow

```
When provider = OpenAI:
    │
    ▼
┌────────────────────────────────┐
│ Send Request to API            │
│                                │
│ URL = OPENAI_BASE_URL          │
│      + /chat/completions       │
│                                │
│ Headers:                       │
│   Authorization: Bearer KEY    │
│   Content-Type: application/json
│                                │
│ Body:                          │
│   model: "gpt-oss-20b"  ← stripped prefix
│   messages: [...]              │
└────────────────────────────────┘
```

**Key insight:** When using `openai/` prefix, claw-code STRIPS the prefix before sending to the API. So:
- `openai/gpt-oss-20b` → sends `gpt-oss-20b` to API ✅
- `openai/deepseek-ai/deepseek-v4-flash` → REJECTED before reaching API ❌

### 4. Why OPENAI_BASE_URL Doesn't Help

Even if we set `OPENAI_BASE_URL=http://127.0.0.1:8082/v1` (pointing to our proxy), claw-code STILL validates the model format BEFORE making the HTTP request. The rejection happens at parse time, not at request time.

```
Timeline:
1. Parse model string     ← REJECTION HAPPENS HERE
2. (never reaches) HTTP request to OPENAI_BASE_URL
```

---

## Solution Architecture

### Approach A: Modify Model Parsing (Recommended)

**Why:** Changes the validation rule to allow multi-slash model IDs.

**Flow after fix:**
```
User Input: --model "openai/deepseek-ai/deepseek-v4-flash"
         │
         ▼
┌─────────────────────────────┐
│ parse_model_with_provider() │
│                             │
│ 1. Split on FIRST '/'       │
│ 2. provider = "openai"      │
│ 3. model = "deepseek-ai/deepseek-v4-flash"
│ 4. VALIDATE: allow '/' in model_id  ← FIX
│ 5. Return provider metadata │
└─────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Send to OPENAI_BASE_URL        │
│ model: "deepseek-ai/deepseek-v4-flash"
│                                │
│ NVIDIA NIM accepts this ✅     │
└────────────────────────────────┘
```

### Approach B: Add NVIDIA as Provider

**Why:** Cleaner separation, env var detection, custom base URL.

**Flow:**
```
User Input: --model "nvidia/deepseek-ai/deepseek-v4-flash"
         │
         ▼
┌──────────────────────────────────┐
│ Provider Detection (mod.rs)      │
│                                  │
│ if starts_with("nvidia/") → NVIDIA ← NEW
│   auth_env = "NVIDIA_API_KEY"    │
│   base_url = "https://integrate.api.nvidia.com/v1"
└──────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Send to NVIDIA API directly    │
│ model: "deepseek-ai/deepseek-v4-flash"
│ Authorization: Bearer nvapi-...│
└────────────────────────────────┘
```

**Advantages:**
- No need for `openai/` prefix hack
- Direct NVIDIA API access
- Can use `NVIDIA_API_KEY` env var
- Cleaner config: `nvidia/deepseek-ai/deepseek-v4-flash`

---

## Detailed Implementation Steps

### Step 1: Clone Source
```bash
git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
```

**Why:** Need source code to modify the binary.

### Step 2: Add NVIDIA Provider (mod.rs)

**File:** `crates/api/src/providers/mod.rs`

**Why:** Register NVIDIA as a recognized provider so claw-code can detect it.

```rust
// Add to ProviderKind enum:
pub enum ProviderKind {
    Anthropic,
    OpenAi,
    Xai,
    DashScope,
    Nvidia,  // ← ADD THIS
}

// Add to resolve_provider():
if canonical.starts_with("nvidia/") {
    return Some(ProviderMetadata {
        provider: ProviderKind::Nvidia,
        auth_env: "NVIDIA_API_KEY",
        base_url_env: "NVIDIA_BASE_URL",
        default_base_url: "https://integrate.api.nvidia.com/v1",
    });
}
```

**Why this location:** This is where all provider detection happens. Adding here means claw-code will recognize `nvidia/` prefix automatically.

### Step 3: Modify Model Parsing (openai_compat.rs)

**File:** `crates/api/src/providers/openai_compat.rs`

**Why:** The current validation rejects slashes in model IDs. We need to allow them for NVIDIA models.

**Option A (Simple):** Remove the slash validation entirely
```rust
// BEFORE:
if model_id.contains('/') {
    return Err("invalid_model_syntax");
}

// AFTER:
// Remove or comment out this validation
// model_id can now contain slashes
```

**Why safe:** The OpenAI API itself validates model names. If we send an invalid model, the API returns an error. We don't need client-side validation.

**Option B (Precise):** Only allow slashes for specific providers
```rust
// Allow slashes only for NVIDIA and OpenAI-compat providers
if model_id.contains('/') && !matches!(provider, ProviderKind::Nvidia | ProviderKind::OpenAi) {
    return Err("invalid_model_syntax");
}
```

### Step 4: Update HTTP Client (client.rs)

**File:** `crates/api/src/client.rs`

**Why:** When provider is NVIDIA, use NVIDIA_API_KEY and NVIDIA_BASE_URL instead of OPENAI_*.

```rust
// Add NVIDIA case:
ProviderKind::Nvidia => {
    let api_key = std::env::var("NVIDIA_API_KEY")
        .or_else(|_| std::env::var("OPENAI_API_KEY"))?;  // fallback
    let base_url = std::env::var("NVIDIA_BASE_URL")
        .unwrap_or_else(|_| "https://integrate.api.nvidia.com/v1".to_string());
    // ... setup HTTP client with these values
}
```

### Step 5: Update Config Schema (lib.rs)

**File:** `crates/config/src/lib.rs`

**Why:** Allow `providerFallbacks` to include NVIDIA provider.

```rust
// In config schema, add nvidia to providerFallbacks enum:
provider_fallbacks: Vec<String>,  // already exists, just needs to accept "nvidia/..." values
```

### Step 6: Build & Test

```bash
cargo build --release
# Binary: target/release/claw.exe

# Test NVIDIA models:
claw --model nvidia/deepseek-ai/deepseek-v4-flash "hello"
claw --model nvidia/meta/llama-3.3-70b-instruct "hello"
claw --model nvidia/qwen/qwen3.5-397b-a17b "hello"
claw --model nvidia/nvidia/llama-3.3-nemotron-super-49b-v1.5 "hello"
claw --model nvidia/mistralai/mistral-large-3-675b-instruct-2512 "hello"
```

---

## Current Workaround Reference

### nvidia_proxy.py (localhost:8082)

**Why it exists:** To test if the proxy approach could work.

**How it works:**
```
claw-code → http://127.0.0.1:8082/v1/chat/completions
                │
                ▼
        ┌───────────────┐
        │ nvidia_proxy   │
        │                │
        │ Model rewrite: │
        │ "deepseek-v4-flash"
        │     ↓          │
        │ "openai/gpt-oss-20b"
        └───────┬───────┘
                │
                ▼
        NVIDIA NIM API
```

**Why it doesn't work with claw-code:**
- claw-code validates model format BEFORE making HTTP request
- The rejection happens at parse time, not request time
- Setting OPENAI_BASE_URL has no effect on validation

**Why keep it:** Fallback for other tools (OpenCode, scripts) that can use it.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing models | Low | High | Test all providers after change |
| NVIDIA API format changes | Low | Medium | Model map in proxy can be updated |
| Binary size increase | None | None | No new dependencies |
| Performance impact | None | None | Validation change is negligible |

---

## Dependencies

- Rust toolchain (cargo) - for building
- claw-code source access - github.com/ultraworkers/claw-code
- NVIDIA API key - already configured
- Testing time - 30 minutes

---

## Keep Current Work

- `nvidia_proxy.py` stays as fallback
- MCP configs unchanged (4 CLIs)
- `settings.json` unchanged
- `.claw/settings.json` unchanged
- All API keys unchanged

---

## Available NVIDIA Models (verified working)

| Short Name | Full NVIDIA ID | Status |
|------------|---------------|--------|
| gpt-oss-20b | openai/gpt-oss-20b | ✅ Works natively |
| llama-3.3-70b | meta/llama-3.3-70b-instruct | ✅ Via proxy |
| qwen3.5-397b | qwen/qwen3.5-397b-a17b | ✅ Via proxy |
| nemotron-super-49b | nvidia/llama-3.3-nemotron-super-49b-v1.5 | ✅ Via proxy |
| mistral-large-3 | mistralai/mistral-large-3-675b-instruct-2512 | ✅ Via proxy |

**Not available on NVIDIA NIM:**
- deepseek-ai/deepseek-v4-flash (timeout)
- minimaxai/minimax-m2.7 (timeout)
- moonshotai/kimi-k2.5 (404)
