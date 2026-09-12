// Swarm Benchmarks - Comprehensive Performance Testing

use codex_engine::{Compression, SwarmEngine, TaskManager};
use criterion::{criterion_group, criterion_main, BatchSize, BenchmarkId, Criterion, Throughput};
use std::hint::black_box;
use std::time::Duration;

// Phase 4 measurements deliberately use fixed inputs and short, bounded runs.
// Criterion only reports a change outside this noise band as a regression. This
// avoids turning ordinary shared-runner variance into a performance signal.
const PHASE4_NOISE_THRESHOLD: f64 = 0.15;
const PHASE4_SIGNIFICANCE_LEVEL: f64 = 0.01;
const PHASE4_SAMPLE_SIZE: usize = 30;
const PHASE4_WARM_UP: Duration = Duration::from_secs(1);
const PHASE4_MEASUREMENT: Duration = Duration::from_secs(3);
const QUEUE_BATCH_SIZES: [usize; 3] = [64, 512, 4_096];
const SWARM_BATCH_SIZES: [usize; 2] = [256, 2_048];
const TASK_PAYLOAD: &[u8] = br#"{"kind":"phase4","payload":"fixed"}"#;

/// Benchmark 1: synchronous task queue round-trip latency.
///
/// A fresh manager is used for each iteration and every submitted result is
/// consumed. This prevents retained results from filling the bounded queue and
/// making later samples measure backpressure (or block indefinitely).
fn bench_task_latency(c: &mut Criterion) {
    let mut group = c.benchmark_group("phase4/task_queue_round_trip");
    group
        .warm_up_time(PHASE4_WARM_UP)
        .measurement_time(PHASE4_MEASUREMENT)
        .sample_size(PHASE4_SAMPLE_SIZE)
        .noise_threshold(PHASE4_NOISE_THRESHOLD)
        .significance_level(PHASE4_SIGNIFICANCE_LEVEL);

    for size in [1_usize, 10, 100, 1_000] {
        group.throughput(Throughput::Elements(size as u64));
        group.bench_with_input(
            BenchmarkId::from_parameter(size),
            &size,
            |b: &mut criterion::Bencher, &size| {
                b.iter_batched_ref(
                    TaskManager::new,
                    |manager| {
                        for _ in 0..size {
                            manager.submit(black_box(TASK_PAYLOAD.to_vec()));
                        }
                        for _ in 0..size {
                            black_box(manager.get_result(0.0).expect(
                                "synchronous identity transport must make each result available",
                            ));
                        }
                    },
                    BatchSize::PerIteration,
                );
            },
        );
    }

    group.finish();
}

/// Benchmark 2: bounded experimental identity-transport throughput.
///
/// A small, fixed worker count limits host contention. Every batch is below the
/// result-queue capacity and is fully drained by `process_batch`, so iterations
/// cannot leak work into later samples. The workers currently return their
/// input unchanged; this measures transport and scheduling, not agent work.
fn bench_throughput(c: &mut Criterion) {
    let mut group = c.benchmark_group("phase4/experimental_identity_transport_throughput");
    group
        .warm_up_time(PHASE4_WARM_UP)
        .measurement_time(PHASE4_MEASUREMENT)
        .sample_size(PHASE4_SAMPLE_SIZE)
        .noise_threshold(PHASE4_NOISE_THRESHOLD)
        .significance_level(PHASE4_SIGNIFICANCE_LEVEL);

    let swarm = SwarmEngine::new(4);
    for batch_size in SWARM_BATCH_SIZES {
        group.throughput(Throughput::Elements(batch_size as u64));
        group.bench_with_input(
            BenchmarkId::new("schedule_and_drain", batch_size),
            &batch_size,
            |b, &batch_size| {
                b.iter(|| {
                    let received = swarm.process_batch(black_box(batch_size));
                    assert_eq!(received, batch_size);
                    black_box(received)
                });
            },
        );
    }

    group.finish();
}

/// Benchmark 3: reproducible queue submission and drain throughput.
///
/// Setup is outside the timed section and creates a fresh manager for every
/// iteration. `PerIteration` bounds retained queue entries while keeping the
/// allocation and synchronization of each queue operation in the measurement.
fn bench_queue_throughput(c: &mut Criterion) {
    let mut group = c.benchmark_group("phase4/task_queue_throughput");
    group
        .warm_up_time(PHASE4_WARM_UP)
        .measurement_time(PHASE4_MEASUREMENT)
        .sample_size(PHASE4_SAMPLE_SIZE)
        .noise_threshold(PHASE4_NOISE_THRESHOLD)
        .significance_level(PHASE4_SIGNIFICANCE_LEVEL);

    for batch_size in QUEUE_BATCH_SIZES {
        group.throughput(Throughput::Elements(batch_size as u64));

        group.bench_with_input(
            BenchmarkId::new("submit", batch_size),
            &batch_size,
            |b, &batch_size| {
                b.iter_batched_ref(
                    TaskManager::new,
                    |manager| {
                        for _ in 0..batch_size {
                            manager.submit(black_box(TASK_PAYLOAD.to_vec()));
                        }
                        assert_eq!(manager.result_count(), batch_size);
                        black_box(manager.result_count())
                    },
                    BatchSize::PerIteration,
                );
            },
        );

        group.bench_with_input(
            BenchmarkId::new("drain_results", batch_size),
            &batch_size,
            |b, &batch_size| {
                b.iter_batched_ref(
                    || {
                        let manager = TaskManager::new();
                        for _ in 0..batch_size {
                            manager.submit(TASK_PAYLOAD.to_vec());
                        }
                        manager
                    },
                    |manager| {
                        let mut received = 0;
                        for _ in 0..batch_size {
                            received += usize::from(manager.get_result(0.0).is_some());
                        }
                        assert_eq!(received, batch_size);
                        black_box(received)
                    },
                    BatchSize::PerIteration,
                );
            },
        );
    }

    group.finish();
}

/// Benchmark 4: Compression
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
                // Log compression failure for debugging
                if let Err(e) = &compressed {
                    eprintln!(
                        "Compression failed in compression_ratio_1mb benchmark: {:?}",
                        e
                    );
                }
                // Return NaN to distinguish from valid compression ratios
                f64::NAN
            }
        });
    });

    group.finish();
}

/// Benchmark 5: Concurrent Agents
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

/// Benchmark 6: Task Manager Operations
/// Tests individual task manager operations
fn bench_task_manager_ops(c: &mut Criterion) {
    let mut group = c.benchmark_group("task_manager_ops");

    group.bench_function("submit_single_task", |b: &mut criterion::Bencher| {
        b.iter_batched_ref(
            TaskManager::new,
            |manager| {
                manager.submit_task(black_box("benchmark_task"));
                black_box(
                    manager
                        .get_result(0.0)
                        .expect("synchronous identity transport must return one result"),
                )
            },
            BatchSize::PerIteration,
        );
    });

    group.bench_function("submit_retrieve_cycle", |b: &mut criterion::Bencher| {
        b.iter_batched_ref(
            TaskManager::new,
            |manager| {
                manager.submit_task(black_box("test"));
                black_box(
                    manager
                        .get_result(0.0)
                        .expect("synchronous identity transport must return one result"),
                )
            },
            BatchSize::PerIteration,
        );
    });

    group.finish();
}

/// Benchmark 7: Compression with Different Data Types
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

/// Benchmark 8: End-to-End Workflow
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
    bench_queue_throughput,
    bench_compression,
    bench_concurrent_agents,
    bench_task_manager_ops,
    bench_compression_patterns,
    bench_e2e_workflow
);

criterion_main!(benches);
