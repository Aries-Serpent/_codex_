# Comprehensive FAQ Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated: 2026-07-08
**Sections:** 60+ frequently asked questions organized by user type

---

## Quick Search

**What's your role?**
- [Data Scientist FAQs](#-data-scientist-faqs)
- [ML Engineer FAQs](#-ml-engineer-faqs)
- [DevOps / SRE FAQs](#-devops--sre-faqs)
- [API Consumer FAQs](#-api-consumer-faqs)
- [End User FAQs](#-end-user-faqs)
- [General FAQs](#-general-faqs)

---

## Data Scientist FAQs

### Training & Model Development

**Q: How do I get started with model training?**

A: Follow these steps:
1. Prepare your data (CSV, JSON, or Hugging Face Dataset)
2. Install: `pip install 'codex-ml[ml]'`
3. Create config YAML file (see `config/base/app.yaml` template)
4. Run: `codex train --config config/my_config.yaml --data data/train.csv`

**Q: What GPUs are recommended?**

A:
- **Development**: Any GPU (GTX 1080 Ti, RTX 3090)
- **Production Training**: A100 (most cost-efficient for large models)
- **Fine-tuning**: RTX 3090 or RTX 4090 sufficient
- **Inference**: T4 or V100 good; A10G best value

**Q: How much memory do I need?**

A:
- BERT-base: 8 GB GPU, 16 GB RAM
- BERT-large: 16 GB GPU, 32 GB RAM
- GPT-2: 12 GB GPU, 24 GB RAM
- 7B LLM: 24 GB GPU, 48 GB RAM (with LoRA: 8 GB)

**Q: Can I train on CPU?**

A: Yes, but it's **very slow** (10-100x slower than GPU). Good for:
- Prototyping with small data (<10k samples)
- Testing code locally before GPU cluster
- Development/debugging

Not recommended for production training.

**Q: How do I handle imbalanced datasets?**

A:
```python
from codex_ml.data import DataBalancer

balancer = DataBalancer()
balanced = balancer.balance(
 dataset,
 strategy='oversampling', # or 'undersampling', 'smote'
 target_ratio=0.5
)
```

**Q: What's the best learning rate?**

A: Start with `2e-5` for fine-tuning, `5e-4` for training from scratch. Use learning rate warmup:
```yaml
training:
 learning_rate: 2e-5
 warmup_steps: 500 # Gradually increase first 500 steps
 warmup_strategy: linear
```

**Q: How do I prevent overfitting?**

A:
1. Use dropout: `dropout: 0.1` in config
2. Add regularization: `weight_decay: 0.01`
3. Early stopping: `patience: 3` (stop if val loss doesn't improve)
4. Data augmentation
5. More training data
6. Smaller model

**Q: Can I use multiple GPUs?**

A: Yes! Codex ML automatically uses all GPUs:
```python
engine = TrainingEngine(
 config='config/training.yaml',
 num_gpus=4, # or 'auto' to use all
 distributed_backend='ddp' # DistributedDataParallel
)
```

**Q: How long should training take?**

A:
- BERT-base, 10k samples: 10-20 minutes (1 GPU)
- BERT-large, 100k samples: 2-4 hours (4 GPUs)
- GPT-2, 1M samples: 1-3 days (8 A100 GPUs)

Use above estimates to sanity-check your training.

### Model Evaluation

**Q: What metrics should I use?**

A: Depends on task:
- **Classification**: Accuracy, F1, precision, recall, AUC-ROC
- **NLP**: BLEU, ROUGE, Perplexity
- **Time series**: MAE, RMSE, MAPE
- **Ranking**: MRR, NDCG

```python
from codex_ml.evaluation import MetricsCalculator

calc = MetricsCalculator(task='classification')
metrics = calc.compute(predictions, labels)
print(metrics)
```

**Q: How do I know if my model is good?**

A:
1. **Baseline comparison**: Compare vs. rule-based or previous model
2. **Human evaluation**: Have SMEs label samples
3. **Statistical significance**: 95% confidence interval on test set
4. **Domain benchmarks**: Compare vs. published numbers
5. **Business metrics**: Does it improve business outcome?

**Q: Should I optimize for accuracy or F1?**

A: Depends on your problem:
- **Balanced classes**: Accuracy is fine
- **Imbalanced classes**: Use F1, precision-recall AUC
- **Cost-sensitive**: Use weighted metrics

Example:
```python
# Imbalanced sentiment (mostly positive)
metrics = evaluator.compute(
 predictions,
 labels,
 metric_type='f1_weighted' # Better for imbalance
)
```

---

## ML Engineer FAQs

### Deployment & Serving

**Q: What's the difference between Ray Serve and Kubernetes?**

A:
| Aspect | Ray Serve | Kubernetes |
|--------|-----------|-----------|
| Complexity | Low | High |
| Scalability | Medium (single cluster) | High (global) |
| Auto-scaling | Simpler | More flexible |
| Cost | Lower | Higher |
| Learning curve | Shallow | Steep |

**Use Ray Serve** for: Startups, single-region deployment, Python-first
**Use Kubernetes** for: Enterprise, multi-region, polyglot services

**Q: How do I scale my deployed model?**

A: Multiple approaches:
```python
# 1. Increase replicas (easiest)
deployment.scale(num_replicas=10)

# 2. Add GPU per replica
deployment = RayServeDeployment(num_gpus=2)

# 3. Enable auto-scaling
deployment.auto_scale(
 min_replicas=2,
 max_replicas=20,
 target_num_ongoing_requests=10
)
```

**Q: How do I handle model updates without downtime?**

A:
```python
# 1. Canary deployment (gradual 5% 10% ... 100%)
canary = CanaryDeployment(
 stable_version='1.0.0',
 canary_version='1.1.0',
 initial_traffic_percent=5,
 increment_percent=10,
 increment_interval_minutes=10
)

# 2. Blue-green deployment (instant switch, easy rollback)
bg = BlueGreenDeployment(
 blue_version='1.0.0', # Current production
 green_version='1.1.0' # New version
)
```

**Q: What latency should I expect?**

A: Typical latencies:
- BERT inference: 40-100ms (1 GPU, batch=1)
- DistilBERT: 20-50ms
- GPT-2: 200-500ms
- Optimize with: quantization (-50%), batching (-70%), caching (-90%)

**Q: How do I monitor model drift?**

A:
```python
from codex_ml.monitoring import ModelPerformanceMonitor

monitor = ModelPerformanceMonitor()
monitor.log_prediction(
 input=text,
 predicted=model.predict(text),
 ground_truth=label # When available
)

# Daily check
if monitor.check_drift()['detected']:
 trigger_retrain()
```

---

## DevOps / SRE FAQs

### Infrastructure

**Q: Should I use Docker or Kubernetes?**

A:
- **Docker Compose**: Local development, small teams (<5 people)
- **Kubernetes**: Production, 24/7 uptime requirement, multi-region

**Q: What's the minimum infrastructure for production?**

A:
```
- 3 API nodes (multi-AZ)
- 1 PostgreSQL DB (RDS, managed)
- 1 Redis cache
- 1 Load balancer
- Object storage (S3/GCS)
- Estimated cost: $500-1000/month
```

**Q: How do I ensure high availability?**

A:
1. **Multiple replicas**: Min 3, max 10
2. **Load balancing**: Round-robin or least-connections
3. **Health checks**: Liveness + readiness probes
4. **Circuit breakers**: Fail gracefully, don't cascade
5. **Backup database**: Multi-AZ, automated snapshots
6. **Disaster recovery**: Restore from backups < 1 hour

**Q: What observability stack do you recommend?**

A:
- **Metrics**: Prometheus (or Datadog)
- **Logs**: ELK Stack or Splunk
- **Traces**: Jaeger or Datadog
- **Dashboards**: Grafana
- **Alerts**: AlertManager or PagerDuty

---

## API Consumer FAQs

### Integration

**Q: How do I authenticate to the API?**

A:
```python
# Header-based (******
headers = {'Authorization': '******'}

# Or use SDK (recommended)
from codex_ml import CodexML
client = CodexML(api_key='sk-proj-...')
```

**Q: What's the rate limit?**

A: Default limits (per API key):
- Free tier: 10 req/minute
- Pro tier: 100 req/minute
- Enterprise: Custom

Contact support for higher limits.

**Q: How do I handle rate limiting?**

A:
```python
from codex_ml import CodexML
from codex_ml.retry import ExponentialBackoff

client = CodexML(
 api_key='...',
 retry_strategy=ExponentialBackoff(max_retries=5)
)
# Automatically retries with exponential backoff
```

**Q: Can I cache predictions?**

A: Yes!
```python
from codex_ml.caching import RequestCache

cache = RequestCache(ttl_seconds=3600) # 1 hour TTL
client = CodexML(api_key='...', cache=cache)

# First call: API
result1 = client.predict(...)

# Same input, different call: cache hit (0ms)
result2 = client.predict(...)
```

**Q: What file formats does the API support?**

A: For batch predictions:
- CSV
- JSON Lines (newline-delimited JSON)
- Excel (.xlsx)
- Up to 100 MB per file

**Q: How long do batch predictions take?**

A:
- 100 samples: 5-10 seconds
- 1000 samples: 30-60 seconds
- 10000 samples: 3-5 minutes
- 100000 samples: 20-40 minutes

---

## End User FAQs

### Web Interface

**Q: How do I upload data?**

A:
1. Click "Upload File"
2. Choose CSV or Excel
3. Map columns to input fields
4. Click "Process"

Max file size: 100 MB

**Q: What's a confidence score?**

A: Shows how certain the model is (0-100%):
- 90%+: Very confident, trust result
- 70-90%: Good confidence
- 50-70%: Be cautious, double-check
- <50%: Low confidence, may be wrong

**Q: Can I export results?**

A: Yes! Multiple formats:
- CSV (data only)
- Excel (with formatting)
- PDF (report format)
- PowerPoint (presentations)

---

## General FAQs

### Account & Billing

**Q: Is there a free tier?**

A: Yes! Free tier includes:
- 1000 predictions/month
- 1 model at a time
- Community support
- Email support (24h response time)

Upgrade for more predictions or priority support.

**Q: What happens if I exceed my limits?**

A: API calls are rejected with 429 status. Options:
1. Wait for next billing period
2. Upgrade plan
3. Request higher limit (contact support)

**Q: Can I cancel anytime?**

A: Yes! No cancellation fees. Your data deleted immediately.

**Q: Do you offer SLAs?**

A: Yes, enterprise customers get:
- 99.9% uptime SLA
- Priority support (1h response time)
- Custom rate limits
- Dedicated account manager

Contact: enterprise@codex-ml.dev

### Data & Privacy

**Q: Is my data encrypted?**

A: Yes!
- In transit: TLS 1.3
- At rest: AES-256
- Backups: Encrypted

**Q: Can you see my predictions?**

A: No! Only you see your data and predictions.

**Q: Where is data stored?**

A: US data centers (by default). EU/APAC options available upon request.

**Q: GDPR compliant?**

A: Yes! Full compliance including:
- Data export
- Right to be forgotten
- Data processing agreements
- Privacy policy transparency

### Features & Troubleshooting

**Q: Which models should I use for my task?**

A:
- **Text Classification**: sentiment-classifier, topic-classifier
- **Named Entity Recognition**: ner-model
- **Question Answering**: qa-model
- **Text Generation**: gpt2-base, distilgpt2

See [Model Comparison](../ROADMAP.md)

**Q: Why are predictions inconsistent?**

A: Possible causes:
1. Model is probabilistic (slight variations expected)
2. Input formatting differs (extra spaces, different casing)
3. Confidence is low (<70%)

Solution: Check input format, retrain if drift detected

**Q: Model doesn't understand my domain**

A: Solutions:
1. **Fine-tune**: Use our domain data (2-3 hours)
2. **Ensemble**: Combine multiple models
3. **Pre-process**: Clean input before prediction

Contact support for custom fine-tuning.

**Q: API is slow/timing out**

A: Try:
1. Reduce request size (batch smaller files)
2. Reduce timeout requirement
3. Check network latency: `ping api.codex-ml.dev`
4. Contact support if issue persists

---

## More Help

- **Video Tutorials**: [YouTube Channel](https://youtube.com/codex-ml)
- **Documentation**: [Full Docs](../index.md)
- **Community**: [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions)
- **Email Support**: [support@codex-ml.dev](mailto:support@codex-ml.dev)

---

**Questions not answered? Ask in [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions) **
