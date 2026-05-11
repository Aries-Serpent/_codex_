// Rust integration tests for TaskQueue
//
// These tests validate high-throughput task distribution

use std::time::Instant;

#[test]
fn test_task_creation() {
    let task = codex_engine::Task::new(
        "task_1".to_string(),
        "analyze".to_string(),
        r#"{"file": "main.py"}"#.to_string()
    );

    assert_eq!(task.id, "task_1");
    assert_eq!(task.task_type, "analyze");
}

#[test]
fn test_queue_basic_operations() {
    let queue = codex_engine::TaskQueue::new();

    let task = codex_engine::Task::new(
        "task_1".to_string(),
        "test".to_string(),
        "{}".to_string()
    );

    queue.submit(task).unwrap();

    let received = queue.receive().unwrap();
    assert!(received.is_some());

    let received_task = received.unwrap();
    assert_eq!(received_task.id, "task_1");

    // Queue should be empty now
    assert!(queue.receive().unwrap().is_none());
}

#[test]
fn test_queue_fifo_order() {
    let queue = codex_engine::TaskQueue::new();

    // Submit 10 tasks
    for i in 0..10 {
        let task = codex_engine::Task::new(
            format!("task_{}", i),
            "test".to_string(),
            "{}".to_string()
        );
        queue.submit(task).unwrap();
    }

    // Receive and verify order
    for i in 0..10 {
        let task = queue.receive().unwrap().unwrap();
        assert_eq!(task.id, format!("task_{}", i));
    }
}

#[test]
fn test_high_throughput() {
    let queue = codex_engine::TaskQueue::new();
    let num_tasks = 10000;

    // Submit 10,000 tasks and measure time
    let start = Instant::now();
    for i in 0..num_tasks {
        let task = codex_engine::Task::new(
            format!("task_{}", i),
            "test".to_string(),
            "{}".to_string()
        );
        queue.submit(task).unwrap();
    }
    let elapsed = start.elapsed();

    // Should complete in < 1 second (acceptance criteria: > 10k tasks/s)
    assert!(elapsed.as_secs_f64() < 1.0, "Submission took {:?} (should be < 1s)", elapsed);

    // Verify all tasks can be received
    let mut count = 0;
    while queue.receive().unwrap().is_some() {
        count += 1;
    }
    assert_eq!(count, num_tasks);
}

#[test]
fn test_concurrent_submission() {
    use std::thread;
    use std::sync::Arc;

    let queue = Arc::new(codex_engine::TaskQueue::new());
    let num_threads = 10;
    let tasks_per_thread = 100;

    let handles: Vec<_> = (0..num_threads)
        .map(|_thread_id| {
            let queue_clone = Arc::clone(&queue);
            thread::spawn(move || {
                for i in 0..tasks_per_thread {
                    let task = codex_engine::Task::new(
                        format!("task_{}_{}", _thread_id, i),
                        "test".to_string(),
                        "{}".to_string()
                    );
                    queue_clone.submit(task).unwrap();
                }
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    // Count received tasks
    let mut count = 0;
    while queue.receive().unwrap().is_some() {
        count += 1;
    }

    assert_eq!(count, num_threads * tasks_per_thread);
}

#[test]
fn test_task_data_integrity() {
    let queue = codex_engine::TaskQueue::new();

    let json_data = r#"{"key": "value", "number": 42, "nested": {"field": "test"}}"#;
    let task = codex_engine::Task::new(
        "task_1".to_string(),
        "complex".to_string(),
        json_data.to_string()
    );

    queue.submit(task).unwrap();

    let received = queue.receive().unwrap().unwrap();
    assert_eq!(received.data, json_data);
}

#[test]
fn test_latency() {
    let queue = codex_engine::TaskQueue::new();

    // Measure submission latency
    let mut latencies = vec![];
    for i in 0..100 {
        let task = codex_engine::Task::new(
            format!("task_{}", i),
            "test".to_string(),
            "{}".to_string()
        );

        let start = Instant::now();
        queue.submit(task).unwrap();
        latencies.push(start.elapsed());
    }

    let avg_latency = latencies.iter().sum::<std::time::Duration>() / latencies.len() as u32;

    // Acceptance criteria: < 1ms latency
    assert!(avg_latency.as_micros() < 1000, "Average latency: {:?}", avg_latency);
}
