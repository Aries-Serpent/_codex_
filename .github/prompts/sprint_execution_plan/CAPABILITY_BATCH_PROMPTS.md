# Capability-Specific Batch Prompts - All 18 Domains

🎯 **COPILOT INSTRUCTION: DOMAIN-FOCUSED REMEDIATION**

@workspace Execute capability-specific improvements across all 18 domains

---

## 1. Checkpointing (Score: 0.84 → 0.90)

**Gaps:**
- Scheduler state not always saved
- RNG sidecar optional (addressed in T4)
- SHA256 validation not strict

**Prompt:**
```python
# File: src/checkpoint_manager.py

class EnhancedCheckpointManager:
    def save_checkpoint(self, state, path):
        # Save model, optimizer, scheduler
        torch.save({
            'model': state.model.state_dict(),
            'optimizer': state.optimizer.state_dict(),
            'scheduler': state.scheduler.state_dict() if state.scheduler else None,
            'epoch': state.epoch,
            'rng': self._get_rng_state(),
            'config': state.config,
        }, path)
        
        # Compute SHA256
        sha256 = self._compute_sha256(path)
        
        # Save manifest
        manifest = {
            'checkpoint_path': str(path),
            'sha256': sha256,
            'timestamp': datetime.now().isoformat(),
            'components': ['model', 'optimizer', 'scheduler', 'rng'],
        }
        with open(path.parent / 'manifest.json', 'w') as f:
            json.dump(manifest, f)
        
        return sha256
    
    def load_checkpoint(self, path, strict=True):
        # Verify SHA256 first
        if strict:
            manifest_path = path.parent / 'manifest.json'
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json.load(f)
                
                actual_sha = self._compute_sha256(path)
                expected_sha = manifest['sha256']
                
                if actual_sha != expected_sha:
                    raise ValueError(
                        f"Checkpoint corruption detected!\n"
                        f"Expected: {expected_sha}\n"
                        f"Actual: {actual_sha}"
                    )
        
        # Load checkpoint
        checkpoint = torch.load(path)
        
        # Restore scheduler if present
        if checkpoint.get('scheduler') and state.scheduler:
            state.scheduler.load_state_dict(checkpoint['scheduler'])
        
        return checkpoint
```

**Tests:**
```python
def test_scheduler_state_saved():
    checkpoint_mgr.save_checkpoint(state, path)
    checkpoint = torch.load(path)
    assert 'scheduler' in checkpoint

def test_sha256_validation_strict():
    # Corrupt checkpoint
    with open(path, 'ab') as f:
        f.write(b'corrupt')
    
    with pytest.raises(ValueError, match="corruption detected"):
        checkpoint_mgr.load_checkpoint(path, strict=True)
```

**Validation:**
```bash
pytest tests/checkpointing/test_enhanced_checkpoint_manager.py
```

---

## 2. Tokenization (Score: 0.83 → 0.90)

**Gaps:**
- Error messages unclear for missing sentencepiece
- No fast tokenizer selection flag
- Vocab diff tooling missing

**Prompt:**
```python
# File: src/codex_ml/tokenization/tokenizer_factory.py

class TokenizerFactory:
    @staticmethod
    def create_tokenizer(path, use_fast=True, **kwargs):
        """Create tokenizer with better error handling."""
        try:
            if use_fast:
                from transformers import AutoTokenizer
                return AutoTokenizer.from_pretrained(path, use_fast=True, **kwargs)
            else:
                from transformers import AutoTokenizer
                return AutoTokenizer.from_pretrained(path, use_fast=False, **kwargs)
        except ImportError as e:
            if 'sentencepiece' in str(e):
                raise ImportError(
                    "SentencePiece not installed.\n"
                    "Install with: pip install sentencepiece\n"
                    "Or: pip install -e .[tokenization]"
                )
            raise
    
    @staticmethod
    def compute_vocab_diff(tokenizer_a, tokenizer_b):
        """Compare vocabularies between two tokenizers."""
        vocab_a = set(tokenizer_a.get_vocab().keys())
        vocab_b = set(tokenizer_b.get_vocab().keys())
        
        return {
            'added': vocab_b - vocab_a,
            'removed': vocab_a - vocab_b,
            'common': vocab_a & vocab_b,
            'diff_count': len(vocab_a.symmetric_difference(vocab_b)),
        }

# Add CLI argument
parser.add_argument('--use-fast-tokenizer', action='store_true', default=True)
parser.add_argument('--no-fast-tokenizer', dest='use_fast_tokenizer', action='store_false')
```

---

## 3. Training Engine (Score: 0.81 → 0.90)

**Gaps:**
- No DDP/FSDP hooks
- Timeout guards missing
- EarlyStopping not default (addressed in T3)

**Prompt:**
```python
# File: src/codex_ml/training/distributed.py

class DistributedTrainer:
    def __init__(self, model, args, **kwargs):
        self.args = args
        
        # Auto-detect distributed setup
        if torch.cuda.device_count() > 1:
            self.setup_distributed()
        
        # Wrap model for distributed
        if args.distributed_backend == 'ddp':
            model = torch.nn.parallel.DistributedDataParallel(model)
        elif args.distributed_backend == 'fsdp':
            from torch.distributed.fsdp import FullyShardedDataParallel
            model = FullyShardedDataParallel(model)
        
        self.model = model
    
    def setup_distributed(self):
        """Initialize distributed training."""
        import torch.distributed as dist
        
        if not dist.is_initialized():
            dist.init_process_group(backend='nccl')
        
        local_rank = int(os.environ.get('LOCAL_RANK', 0))
        torch.cuda.set_device(local_rank)

# Add timeout wrapper
class TimeoutTrainer:
    def train(self, max_duration_seconds=None):
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Training exceeded {max_duration_seconds}s")
        
        if max_duration_seconds:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(max_duration_seconds)
        
        try:
            return super().train()
        finally:
            if max_duration_seconds:
                signal.alarm(0)  # Cancel alarm
```

---

## 4. Evaluation & Metrics (Score: 0.74 → 0.90)

**Gaps:**
- Limited task registration
- NDJSON output not aligned with training
- No --limit, --batch-size flags

**Prompt:**
```python
# File: src/hhg_logistics/eval/enhanced_harness.py

class EnhancedEvalHarness:
    def __init__(self, model, tasks, limit=None, batch_size=1):
        self.model = model
        self.tasks = tasks
        self.limit = limit
        self.batch_size = batch_size
    
    def evaluate(self, output_path=None):
        """Evaluate with NDJSON output."""
        results = {}
        
        for task_name in self.tasks:
            task = self._load_task(task_name)
            
            # Limit number of samples
            if self.limit:
                task.limit = self.limit
            
            # Run evaluation
            task_results = task.evaluate(self.model, batch_size=self.batch_size)
            results[task_name] = task_results
            
            # Write NDJSON
            if output_path:
                self._write_ndjson(task_name, task_results, output_path)
        
        return results
    
    def _write_ndjson(self, task_name, results, output_path):
        """Write results in same format as training logs."""
        with open(output_path, 'a') as f:
            record = {
                'timestamp': datetime.now().isoformat(),
                'phase': 'eval',
                'task': task_name,
                'metrics': results,
            }
            f.write(json.dumps(record) + '\n')

# CLI additions
parser.add_argument('--eval-tasks', nargs='+', default=['hellaswag', 'arc_easy'])
parser.add_argument('--eval-limit', type=int, default=None)
parser.add_argument('--eval-batch-size', type=int, default=8)
```

---

## 5. Data Pipeline (Score: 0.72 → 0.90)

**Gaps:**
- Streaming ingestion partial
- Cache invalidation not explicit
- No dataset checksums (addressed in T6)

**Prompt:**
```python
# File: src/codex_ml/data/streaming_dataset.py

class StreamingDataset:
    def __init__(self, path, streaming=True, cache_dir=None):
        self.path = path
        self.streaming = streaming
        self.cache_dir = cache_dir or Path.home() / '.cache/codex_ml'
        
        if streaming:
            from datasets import load_dataset
            self.dataset = load_dataset(path, streaming=True)
        else:
            self.dataset = self._load_with_cache()
    
    def _load_with_cache(self):
        """Load dataset with explicit caching."""
        cache_path = self.cache_dir / self._get_cache_key()
        
        if cache_path.exists():
            # Validate cache
            if self._is_cache_valid(cache_path):
                return torch.load(cache_path)
            else:
                print("⚠️ Cache invalid, rebuilding...")
                cache_path.unlink()
        
        # Load fresh
        from datasets import load_dataset
        dataset = load_dataset(self.path)
        
        # Save to cache
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(dataset, cache_path)
        
        return dataset
    
    def _get_cache_key(self):
        """Generate cache key from dataset path."""
        import hashlib
        return hashlib.sha256(str(self.path).encode()).hexdigest()[:16]
    
    def _is_cache_valid(self, cache_path):
        """Check if cache is still valid."""
        # Check age
        age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        if age.days > 7:  # Cache expires after 7 days
            return False
        
        return True
    
    def invalidate_cache(self):
        """Explicitly invalidate cache."""
        cache_path = self.cache_dir / self._get_cache_key()
        if cache_path.exists():
            cache_path.unlink()
            print(f"✓ Cache invalidated: {cache_path}")

# CLI additions
parser.add_argument('--streaming', action='store_true')
parser.add_argument('--no-cache', action='store_true')
parser.add_argument('--invalidate-cache', action='store_true')
```

---

## 6. Logging & Tracking (Score: 0.76 → 0.90)

**Gaps:**
- W&B may default to online (addressed in T2)
- NVML metrics optional
- TensorBoard path variability

**Prompt:**
```python
# File: src/codex_ml/monitoring/unified_logger.py

class UnifiedLogger:
    def __init__(self, run_name, log_dir='logs', backends=['ndjson', 'tensorboard']):
        self.run_name = run_name
        self.log_dir = Path(log_dir)
        self.backends = {}
        
        # NDJSON backend (always available)
        if 'ndjson' in backends:
            ndjson_path = self.log_dir / f"{run_name}.ndjson"
            self.backends['ndjson'] = NDJSONWriter(ndjson_path)
        
        # TensorBoard backend
        if 'tensorboard' in backends:
            from torch.utils.tensorboard import SummaryWriter
            tb_dir = self.log_dir / 'tensorboard' / run_name
            self.backends['tensorboard'] = SummaryWriter(tb_dir)
        
        # W&B backend (offline by default)
        if 'wandb' in backends:
            import wandb
            mode = os.getenv('WANDB_MODE', 'offline')
            wandb.init(name=run_name, mode=mode)
            self.backends['wandb'] = wandb
        
        # NVML metrics (optional)
        self.nvml_available = self._check_nvml()
    
    def log(self, metrics, step=None):
        """Log to all backends."""
        # Add system metrics if NVML available
        if self.nvml_available:
            metrics.update(self._get_gpu_metrics())
        
        # Write to all backends
        for backend_name, backend in self.backends.items():
            try:
                if backend_name == 'ndjson':
                    backend.write(metrics)
                elif backend_name == 'tensorboard':
                    for key, value in metrics.items():
                        backend.add_scalar(key, value, step)
                elif backend_name == 'wandb':
                    backend.log(metrics, step=step)
            except Exception as e:
                print(f"⚠️ Failed to log to {backend_name}: {e}")
    
    def _check_nvml(self):
        """Check if NVML (GPU metrics) available."""
        try:
            import pynvml
            pynvml.nvmlInit()
            return True
        except:
            return False
    
    def _get_gpu_metrics(self):
        """Get GPU utilization metrics."""
        import pynvml
        metrics = {}
        for i in range(pynvml.nvmlDeviceGetCount()):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            metrics[f'gpu_{i}_utilization'] = util.gpu
            metrics[f'gpu_{i}_memory_used_gb'] = mem.used / 1e9
        
        return metrics

# CLI additions
parser.add_argument('--log-backends', nargs='+', default=['ndjson', 'tensorboard'])
parser.add_argument('--log-system-metrics', action='store_true')
```

---

## 7. Configuration (Score: 0.79 → 0.90)

**Gaps:**
- Sweep orchestration not integrated
- Schema validation not enforced everywhere

**Prompt:**
```python
# File: src/codex_ml/config/validation.py

from pydantic import BaseModel, validator
from typing import Optional, List

class TrainingConfig(BaseModel):
    """Validated training configuration."""
    
    # Required fields
    model_name: str
    data_path: str
    output_dir: str
    
    # Training hyperparameters
    num_epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 5e-5
    
    # Optional fields
    eval_dataset: Optional[str] = None
    checkpoint_every: int = 1000
    log_every: int = 100
    
    # Validators
    @validator('learning_rate')
    def lr_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('learning_rate must be positive')
        return v
    
    @validator('batch_size')
    def batch_size_reasonable(cls, v):
        if v < 1 or v > 1024:
            raise ValueError('batch_size must be between 1 and 1024')
        return v

def load_validated_config(config_path):
    """Load and validate configuration."""
    from omegaconf import OmegaConf
    
    # Load with Hydra/OmegaConf
    cfg = OmegaConf.load(config_path)
    
    # Validate with Pydantic
    try:
        validated = TrainingConfig(**cfg)
        return validated
    except Exception as e:
        print(f"❌ Config validation failed: {e}")
        raise

# Sweep support
from hydra import compose, initialize

def run_sweep(sweep_config):
    """Run hyperparameter sweep."""
    for params in generate_sweep_params(sweep_config):
        with initialize(config_path="configs"):
            cfg = compose(config_name="train", overrides=params)
            
            # Validate
            validated_cfg = TrainingConfig(**cfg)
            
            # Run training
            train(validated_cfg)
```

---

## 8. Safety & Security (Score: 0.61 → 0.90)

**Comprehensive Security Enhancement:**

```python
# File: src/codex_ml/security/security_manager.py

class SecurityManager:
    def __init__(self):
        self.sanitizer = PromptSanitizer()  # From T5
        self.secret_detector = self._init_secret_detector()
        self.audit_log = []
    
    def _init_secret_detector(self):
        """Initialize secret detection."""
        try:
            from detect_secrets import SecretsCollection
            from detect_secrets.settings import default_settings
            return SecretsCollection()
        except ImportError:
            print("⚠️ detect-secrets not installed")
            return None
    
    def check_input(self, text, source='user'):
        """Comprehensive input security check."""
        checks = {
            'prompt_injection': self.sanitizer.is_safe(text),
            'secret_leakage': self._check_secrets(text),
            'size_limit': len(text) < 100000,  # 100KB limit
        }
        
        # Log security event
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'checks': checks,
            'passed': all(checks.values()),
        })
        
        if not all(checks.values()):
            failed = [k for k, v in checks.items() if not v]
            raise SecurityError(f"Security checks failed: {failed}")
        
        return True
    
    def _check_secrets(self, text):
        """Check for accidentally exposed secrets."""
        if not self.secret_detector:
            return True
        
        # Common secret patterns
        patterns = [
            r'sk-[A-Za-z0-9]{20,}',  # API keys
            r'ghp_[A-Za-z0-9]{36}',  # GitHub tokens
            r'AKIA[0-9A-Z]{16}',  # AWS keys
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return False
        
        return True
    
    def export_audit_log(self, path):
        """Export security audit log."""
        with open(path, 'w') as f:
            for event in self.audit_log:
                f.write(json.dumps(event) + '\n')
```

---

## Batch Execution Command

```
@workspace Execute all capability enhancements

File: .github/prompts/sprint_execution_plan/CAPABILITY_BATCH_PROMPTS.md

Domains:
1. Checkpointing (scheduler, SHA256)
2. Tokenization (fast tokenizer, vocab diff)
3. Training (DDP/FSDP, timeout)
4. Evaluation (NDJSON, limits)
5. Data Pipeline (streaming, cache)
6. Logging (unified, NVML)
7. Configuration (validation, sweeps)
8. Security (comprehensive checks)

Execute in parallel where possible.
Validate each domain independently.
Target: All scores ≥0.90
```

🤖 **Copilot:** Systematically improve all 18 capability domains with self-validation
