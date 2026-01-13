// Swarm Benchmarks - Comprehensive Performance Testing
// Phase 2: Performance Benchmarking

use codex_engine::{Compression, SwarmEngine, TaskManager};
use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion};
use std::time::Duration;

/// Benchmark 1: Task Latency
/// Tests latency for various batch sizes (1, 10, 100, 1000 tasks)
fn bench_task_latency(c: &mut Criterion) {
    let mut group = c.benchmark_group("task_latency");
    group.measurement_time(Duration::from_secs(10));

    for size in [1, 10, 100, 1000].iter() {
        group.bench_with_input(
            BenchmarkId::from_parameter(size),
            size,
            |b: &mut criterion::Bencher, &size| {
                let task_manager = TaskManager::new();
                b.iter(|| {
                    for i in 0..size {
                        task_manager.submit_task(black_box(&format!("task_{}", i)));
                    }
                });
            },
        );
    }

    group.finish();
}

/// Benchmark 2: Throughput
/// Tests throughput with 10k tasks target
fn bench_throughput(c: &mut Criterion) {
    let mut group = c.benchmark_group("throughput");
    group.measurement_time(Duration::from_secs(20));
    group.sample_size(50);

    let swarm = SwarmEngine::new(1000); // 1000 agents

    group.bench_function("10k_tasks", |b: &mut criterion::Bencher| {
        b.iter(|| swarm.process_batch(black_box(10_000)));
    });

    group.finish();
}

/// Benchmark 3: Compression
/// Tests compression performance with 1MB data
fn bench_compression(c: &mut Criterion) {
    let mut group = c.benchmark_group("compression");
    group.measurement_time(Duration::from_secs(10));

    // Create 1MB of compressible data
    let data_1mb: Vec<u8> = vec![b'A'; 1_000_000];

    group.bench_function("compress_1mb", |b: &mut criterion::Bencher| {
        b.iter(|| Compression::compress(black_box(&data_1mb)));
    });

    group.bench_function("decompress_1mb", |b: &mut criterion::Bencher| {
        let compressed = Compression::compress(&data_1mb);
        b.iter(|| {
            if let Ok(compressed_data) = &compressed {
                Compression::decompress(black_box(compressed_data))
            } else {
                Ok(Vec::new())
            }
        });
    });

    group.bench_function("compression_ratio_1mb", |b: &mut criterion::Bencher| {
        b.iter(|| {
            let compressed = Compression::compress(black_box(&data_1mb));
            if let Ok(compressed_data) = &compressed {
                Compression::ratio(&data_1mb, compressed_data)
            } else {
                0.0
            }
        });
    });

    group.finish();
}

/// Benchmark 4: Concurrent Agents
/// Tests performance with varying agent counts (100, 500, 1000)
fn bench_concurrent_agents(c: &mut Criterion) {
    let mut group = c.benchmark_group("concurrent_agents");
    group.measurement_time(Duration::from_secs(30));
    group.sample_size(20);

    for agent_count in [100, 500, 1000].iter() {
        group.bench_with_input(
            BenchmarkId::from_parameter(agent_count),
            agent_count,
            |b: &mut criterion::Bencher, &count| {
                let swarm = SwarmEngine::new(count);
                b.iter(|| swarm.execute_parallel(black_box(1000)));
            },
        );
    }

    group.finish();
}

/// Benchmark 5: Task Manager Operations
/// Tests individual task manager operations
fn bench_task_manager_ops(c: &mut Criterion) {
    let mut group = c.benchmark_group("task_manager_ops");

    let manager = TaskManager::new();

    group.bench_function("submit_single_task", |b: &mut criterion::Bencher| {
        b.iter(|| manager.submit_task(black_box("benchmark_task")));
    });

    group.bench_function("submit_retrieve_cycle", |b: &mut criterion::Bencher| {
        b.iter(|| {
            let _id = manager.submit_task(black_box("test"));
            manager.get_result(1.0)
        });
    });

    group.finish();
}

/// Benchmark 6: Compression with Different Data Types
/// Tests compression on various data patterns
fn bench_compression_patterns(c: &mut Criterion) {
    let mut group = c.benchmark_group("compression_patterns");

    // Highly compressible data (repetitive)
    let repetitive_data = vec![b'X'; 100_000];

    // JSON-like structured data
    let json_data = r#"{"id": 1, "type": "task", "data": "test"}"#.repeat(2000).into_bytes();

    // Random data (low compression)
    let random_data: Vec<u8> = (0..100_000).map(|i| (i % 256) as u8).collect();

    group.bench_function("compress_repetitive", |b: &mut criterion::Bencher| {
        b.iter(|| Compression::compress(black_box(&repetitive_data)));
    });

    group.bench_function("compress_json", |b: &mut criterion::Bencher| {
        b.iter(|| Compression::compress(black_box(&json_data)));
    });

    group.bench_function("compress_random", |b: &mut criterion::Bencher| {
        b.iter(|| Compression::compress(black_box(&random_data)));
    });

    group.finish();
}

/// Benchmark 7: End-to-End Workflow
/// Tests complete task processing pipeline
fn bench_e2e_workflow(c: &mut Criterion) {
    let mut group = c.benchmark_group("e2e_workflow");
    group.measurement_time(Duration::from_secs(15));

    group.bench_function(
        "complete_pipeline_100_tasks",
        |b: &mut criterion::Bencher| {
            let swarm = SwarmEngine::new(100);
            b.iter(|| swarm.process_batch(black_box(100)));
        },
    );

    group.finish();
}

criterion_group!(
    benches,
    bench_task_latency,
    bench_throughput,
    bench_compression,
    bench_concurrent_agents,
    bench_task_manager_ops,
    bench_compression_patterns,
    bench_e2e_workflow
);

criterion_main!(benches);
