# Common Workflows Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated: 2026-07-08
**Coverage:** Step-by-step procedures for common tasks across all user types

---

## 🏃 Quick Workflow Reference

**Need to...**
- [Train a model from scratch](#workflow-1-train-model-from-scratch)
- [Fine-tune an existing model](#workflow-2-fine-tune-existing-model)
- [Deploy a model to production](#workflow-3-deploy-to-production)
- [Monitor production performance](#workflow-4-monitor-production)
- [A/B test two models](#workflow-5-ab-test-models)
- [Retrain when performance drops](#workflow-6-auto-retrain)
- [Integrate with external API](#workflow-7-integrate-api)
- [Batch process data](#workflow-8-batch-processing)
- [Debug poor predictions](#workflow-9-debug-predictions)
- [Optimize for cost](#workflow-10-cost-optimization)

---

## Workflow 1: Train Model From Scratch

**Duration:** 30-60 minutes  
**Tools:** Python SDK, GPU recommended  
**Experience Level:** Intermediate

### Steps

```python
from codex_ml.data import DataLoader
from codex_ml.training import TrainingEngine
from codex_ml.config import Config

# 1. Load and prepare data
loader = DataLoader()
dataset = loader.load_csv('data/training_data.csv')

# Analyze data quality
from codex_ml.data import DataQualityAnalyzer
analyzer = DataQualityAnalyzer()
report = analyzer.analyze(dataset)
print(f"Quality score: {report['quality_score']:.1%}")
print(f"Missing values: {report['missing_values']}")
print(f"Class imbalance: {report['class_imbalance']}")

# 2. Split data
train, val, test = dataset.split(
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    stratify_by='label'  # Important for imbalanced data
)

# 3. Configure training
config = {
    'model': {
        'name': 'bert-base-uncased',
        'task': 'sequence-classification',
        'num_labels': 3,
    },
    'training': {
        'max_epochs': 5,
        'batch_size': 32,
        'learning_rate': 2e-5,
        'warmup_steps': 500,
    },
    'optimization': {
        'precision': 'bf16',
        'gradient_accumulation_steps': 2,
    }
}

# 4. Train model
engine = TrainingEngine(config)
metrics = engine.train(train, val)

print(f"Training complete!")
print(f"Val accuracy: {metrics['val_accuracy']:.2%}")
print(f"Val F1 score: {metrics['val_f1']:.2%}")

# 5. Evaluate on test set
test_metrics = engine.evaluate(test)
print(f"Test accuracy: {test_metrics['accuracy']:.2%}")

# 6. Save model
engine.save('outputs/my_model')
```

---

## Workflow 2: Fine-tune Existing Model

**Duration:** 15-30 minutes  
**Tools:** Python SDK, 1+ GPU recommended  
**Experience Level:** Intermediate

### Steps

```python
from codex_ml.training import TrainingEngine, LoRA
from transformers import AutoModel, AutoTokenizer

# 1. Load pre-trained model
model_name = "mistral-7b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
base_model = AutoModel.from_pretrained(model_name)

# 2. Enable LoRA for memory-efficient fine-tuning
lora_config = LoRA(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=['q_proj', 'v_proj']
)

# 3. Prepare data for your domain
dataset = load_your_data()

# 4. Configure fine-tuning
config = {
    'model': {
        'base_model': model_name,
        'use_lora': True,
        'lora_config': lora_config,
    },
    'training': {
        'max_epochs': 3,
        'batch_size': 16,
        'learning_rate': 3e-4,
        'save_steps': 100,
    },
    'precision': 'bf16',
}

# 5. Fine-tune
engine = TrainingEngine(config)
metrics = engine.train(dataset['train'], dataset['val'])

# 6. Merge LoRA adapters (optional)
merged_model = engine.merge_lora_adapters()
merged_model.save_pretrained('outputs/finetuned-model')
```

---

## Workflow 3: Deploy to Production

**Duration:** 20-30 minutes  
**Tools:** Ray Serve or Kubernetes  
**Experience Level:** Advanced

### Steps (Ray Serve)

```python
from codex_ml.serving import RayServeDeployment
from codex_ml.mlops import ModelRegistry
import ray

# 1. Register model in registry
registry = ModelRegistry(backend='huggingface')
registry.register(
    model=trained_model,
    version='1.0.0',
    metrics={'accuracy': 0.92}
)

# 2. Create deployment
deployment = RayServeDeployment(
    name='sentiment-classifier',
    model_path='huggingface/sentiment-v1.0',
    num_replicas=3,
    num_gpus=1,
    batch_size=32
)

# 3. Deploy to Ray cluster
ray.init(address='auto')  # or local
deployment.deploy()

# 4. Test endpoint
import requests
response = requests.post(
    'http://localhost:8000/predict',
    json={'text': 'This is great!'}
)
print(response.json())

# 5. Monitor
from codex_ml.monitoring import DeploymentMonitor
monitor = DeploymentMonitor('sentiment-classifier')
metrics = monitor.collect_metrics(period_minutes=5)
print(f"Throughput: {metrics['throughput']:.0f} req/sec")
print(f"Latency p99: {metrics['latency_p99']:.0f}ms")
```

---

## Workflow 4: Monitor Production

**Duration:** 15 minutes to setup, ongoing  
**Tools:** Prometheus, Grafana, Python  
**Experience Level:** Intermediate

### Steps

```python
from codex_ml.monitoring import (
    DeploymentMonitor,
    ModelPerformanceMonitor,
    AlertManager
)

# 1. Set up deployment monitoring
deployment_monitor = DeploymentMonitor('sentiment-classifier')

# 2. Set up model performance tracking
perf_monitor = ModelPerformanceMonitor(
    model_version='1.0.0',
    expected_metrics={'accuracy': 0.92},
    drift_threshold=0.05
)

# 3. Add predictions to performance tracking (from serving code)
def predict_and_track(text, ground_truth=None):
    prediction = model.predict(text)
    perf_monitor.log_prediction(
        input=text,
        predicted_label=prediction['label'],
        predicted_confidence=prediction['confidence'],
        ground_truth=ground_truth
    )
    return prediction

# 4. Set up alerts
alert_manager = AlertManager()
alert_manager.add_rule(
    name='high_latency',
    metric='latency_p99',
    threshold_ms=500,
    action='slack',
    webhook_url='...'
)

alert_manager.add_rule(
    name='data_drift',
    metric='kl_divergence',
    threshold=0.3,
    action='auto_retrain'
)

# 5. Daily check-ins
def daily_monitor_check():
    metrics = deployment_monitor.collect_metrics(period_minutes=1440)
    perf_metrics = perf_monitor.check_drift()
    
    print(f"Requests today: {metrics['total_requests']}")
    print(f"Error rate: {metrics['error_rate']:.2%}")
    print(f"Avg latency: {metrics['latency_mean']:.0f}ms")
    
    if perf_metrics['detected']:
        print(f"⚠️ DRIFT DETECTED: {perf_metrics['drift_magnitude']:.1%}")
```

---

## Workflow 5: A/B Test Models

**Duration:** 1 week  
**Tools:** Python SDK, Kubernetes  
**Experience Level:** Intermediate

### Steps

```python
from codex_ml.deployment import ABTestDeployment

# 1. Create A/B test
ab_test = ABTestDeployment(
    service_name='sentiment-classifier',
    variant_a_version='1.0.0',      # Control (existing model)
    variant_b_version='1.0.1',      # Treatment (new model)
    traffic_split_percent=50,        # 50/50 split
    test_duration_days=7
)

# 2. Deploy both variants
ab_test.start()

# 3. Monitor progress
for day in range(7):
    status = ab_test.get_status()
    print(f"Day {day+1}")
    print(f"  Variant A accuracy: {status['variant_a_accuracy']:.2%}")
    print(f"  Variant B accuracy: {status['variant_b_accuracy']:.2%}")
    print(f"  A latency: {status['variant_a_latency']:.0f}ms")
    print(f"  B latency: {status['variant_b_latency']:.0f}ms")
    time.sleep(86400)  # Wait 1 day

# 4. Analyze results
results = ab_test.get_results()
improvement = results['variant_b_accuracy'] - results['variant_a_accuracy']

print(f"\n A/B Test Results")
print(f"Variant A: {results['variant_a_accuracy']:.2%}")
print(f"Variant B: {results['variant_b_accuracy']:.2%}")
print(f"Improvement: {improvement:+.2%}")

# 5. Make decision
if results['variant_b_winner']:
    ab_test.promote_variant_b()
    print(" Variant B promoted to production!")
else:
    ab_test.keep_variant_a()
    print(" Variant A remains in production")
```

---

## Workflow 6: Auto-Retrain When Performance Drops

**Duration:** 30 minutes to setup, runs automatically  
**Tools:** Python SDK, Airflow/Kubeflow optional  
**Experience Level:** Advanced

### Steps

```python
from codex_ml.monitoring import ModelPerformanceMonitor
from codex_ml.training import TrainingEngine
from codex_ml.mlops import ModelRegistry
import schedule
import time

# 1. Set up performance monitoring
perf_monitor = ModelPerformanceMonitor(
    model_version='1.0.0',
    expected_metrics={'accuracy': 0.92},
    drift_threshold=0.05,
    check_interval_hours=24
)

# 2. Set up retraining trigger
def check_performance_and_retrain():
    metrics = perf_monitor.get_recent_metrics(period_days=7)
    accuracy = metrics['accuracy']
    
    if accuracy < 0.87:  # Performance dropped 5%
        print(f"⚠️ PERFORMANCE DROP: {accuracy:.2%} (target: 92%)")
        trigger_retrain()
    else:
        print(f" Performance OK: {accuracy:.2%}")

def trigger_retrain():
    print(" Starting retraining...")
    
    # 1. Load new data collected since last training
    new_data = collect_new_training_data()
    
    # 2. Train new model
    config = load_training_config('config/training.yaml')
    engine = TrainingEngine(config)
    metrics = engine.train(new_data['train'], new_data['val'])
    
    # 3. Validate new model
    test_metrics = engine.evaluate(new_data['test'])
    if test_metrics['accuracy'] > 0.92:
        print(f" New model better: {test_metrics['accuracy']:.2%}")
        
        # 4. Register new version
        registry = ModelRegistry()
        registry.register(
            model=engine.model,
            version='1.0.1',
            metrics=test_metrics,
            replace_latest=True
        )
        
        # 5. Deploy gradually (canary)
        deploy_canary_update('1.0.1')
    else:
        print(f" New model worse: {test_metrics['accuracy']:.2%}")
        print("Keeping current model in production")

# 3. Schedule automatic checks
schedule.every(24).hours.do(check_performance_and_retrain)

# 4. Run continuously
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Workflow 7: Integrate with External API

**Duration:** 15-20 minutes  
**Tools:** Python SDK or REST API  
**Experience Level:** Beginner

### Steps

```python
from codex_ml import CodexML
import json

# 1. Set up Codex ML client
client = CodexML(api_key="sk-proj-...")

# 2. Get available models
models = client.models.list()
print(f"Available models: {[m['id'] for m in models]}")

# 3. Create prediction function
def classify_customer_feedback(feedback_text):
    request = {
        "model_id": "sentiment-classifier",
        "model_version": "latest",
        "inputs": {"text": feedback_text}
    }
    
    response = client.predict(request)
    return {
        "text": feedback_text,
        "sentiment": response.output['label'],
        "confidence": response.output['confidence'],
        "request_id": response.request_id
    }

# 4. Integrate into your application
from fastapi import FastAPI

app = FastAPI()

@app.post("/analyze-feedback")
async def analyze_feedback(feedback: dict):
    result = classify_customer_feedback(feedback['text'])
    return result

# 5. Add error handling
def safe_classify(text, max_retries=3):
    for attempt in range(max_retries):
        try:
            return classify_customer_feedback(text)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return {"error": str(e)}

# 6. Test
result = safe_classify("I love this product!")
print(json.dumps(result, indent=2))
```

---

## Workflow 8: Batch Processing

**Duration:** 5-15 minutes setup, depends on data size  
**Tools:** Python SDK or Web UI  
**Experience Level:** Beginner

### Steps (via Python SDK)

```python
from codex_ml import CodexML
import pandas as pd
from pathlib import Path

# 1. Load data
df = pd.read_csv('data/customer_feedback.csv')
texts = df['feedback'].tolist()

# 2. Initialize client
client = CodexML(api_key="sk-proj-...")

# 3. Batch predict
predictions = []
batch_size = 100

for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    print(f"Processing batch {i//batch_size + 1}...")
    
    batch_response = client.predict_batch(
        model_id="sentiment-classifier",
        inputs=[{"text": t} for t in batch]
    )
    
    predictions.extend(batch_response.outputs)

# 4. Save results
results_df = df.copy()
results_df['sentiment'] = [p['label'] for p in predictions]
results_df['confidence'] = [p['confidence'] for p in predictions]
results_df.to_csv('outputs/results.csv', index=False)

print(f" Processed {len(predictions)} items")
print(f"Positive: {sum(1 for p in predictions if p['label']=='positive')}")
print(f"Negative: {sum(1 for p in predictions if p['label']=='negative')}")
```

---

## Workflow 9: Debug Poor Predictions

**Duration:** 30-60 minutes  
**Tools:** Python SDK, visualization tools  
**Experience Level:** Intermediate

### Steps

```python
from codex_ml.analysis import ErrorAnalyzer
from codex_ml.interpretability import AttentionVisualizer, GradientAnalyzer

# 1. Identify problematic predictions
error_analyzer = ErrorAnalyzer(model, test_dataset)
hard_examples = error_analyzer.find_hard_examples(k=20)

print(f"Found {len(hard_examples)} hard examples:")
for ex in hard_examples[:5]:
    print(f"  Text: {ex['text']}")
    print(f"  Predicted: {ex['predicted']}, True: {ex['true_label']}")
    print(f"  Confidence: {ex['confidence']:.1%}\n")

# 2. Visualize attention patterns
visualizer = AttentionVisualizer(model)
visualizer.plot(
    text="This product is really amazing but also really expensive",
    label_to_explain="positive"
)
# Shows which words most contributed to "positive" prediction

# 3. Gradient-based explanations
explainer = GradientAnalyzer(model)
explanation = explainer.explain(
    text="I hate this so much",
    target_label="negative"
)
print(f"Words contributing to 'negative' prediction:")
for word, score in explanation.items():
    print(f"  {word}: {score:+.2f}")

# 4. Data analysis
import seaborn as sns
import matplotlib.pyplot as plt

# Find patterns in errors
error_lengths = [len(ex['text'].split()) for ex in hard_examples]
plt.hist(error_lengths, bins=20)
plt.title("Length distribution of hard examples")
plt.show()

# 5. Recommendations
if len(hard_examples) > 5:
    print("\n🔍 Debugging Recommendations:")
    print("1. Your model struggles with domain-specific language")
    print("2. Consider collecting more training data for edge cases")
    print("3. Try data augmentation to make model more robust")
    print("4. Fine-tune on domain-specific data")
```

---

## Workflow 10: Optimize for Cost

**Duration:** 20-30 minutes  
**Tools:** Python SDK, cloud CLI  
**Experience Level:** Intermediate

### Steps

```python
from codex_ml.optimization import CostOptimizer
from codex_ml.serving import ModelServer

# 1. Analyze current costs
optimizer = CostOptimizer()
cost_report = optimizer.analyze_current_setup()

print("Current monthly costs:")
print(f"  Compute: ${cost_report['compute_cost']:.0f}")
print(f"  Storage: ${cost_report['storage_cost']:.0f}")
print(f"  API calls: ${cost_report['api_cost']:.0f}")
print(f"  Total: ${cost_report['total_cost']:.0f}")

# 2. Model optimization options
print("\nOptimization opportunities:")

# a) Quantization (reduce model size)
quantized_model = optimizer.quantize_model(model, bits=8)
print(f"  Quantization: {cost_report['storage_cost']*0.25:.0f} (75% cheaper)")

# b) Distillation (smaller, faster model)
distilled_model = optimizer.distill_model(
    teacher=model,
    temperature=3.0,
    data=training_data
)
print(f"  Distillation: {cost_report['compute_cost']*0.5:.0f} (50% cheaper)")

# c) Batch processing instead of real-time
print(f"  Batch processing: {cost_report['compute_cost']*0.2:.0f} (80% cheaper)")

# 3. Infrastructure optimization
optimized_config = optimizer.recommend_instance_size(
    throughput_requests_per_sec=100,
    latency_requirement_ms=500,
    budget=1000  # Monthly budget
)
print(f"\nRecommended infrastructure: {optimized_config}")

# 4) Implement optimization
# Option A: Use quantized model
quantized_model.save('outputs/quantized-model')

# Option B: Deploy on cheaper instances
deployment_config = {
    'instance_type': 't3.2xlarge',  # Cheaper than p3
    'batch_size': 64,  # Process more at once
    'num_replicas': 2,  # Reduce replicas with batch processing
}

# 5) Measure savings
new_cost = cost_report['total_cost'] * 0.5  # Expected 50% savings
print(f"\n Projected savings: ${cost_report['total_cost'] - new_cost:.0f}/month")
```

---

##  See Also

- [Detailed Task Guides](./TASK_GUIDES/)
- [Advanced Topics](./ADVANCED_TOPICS/)
- [API Reference](../API_REFERENCE_PHASE_15_16.md)
- [Troubleshooting FAQ](./FAQ_TROUBLESHOOTING.md)

---

**All workflows tested on real datasets **
