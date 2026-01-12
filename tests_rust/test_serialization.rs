// Rust integration tests for Serialization

use std::time::Instant;

#[test]
fn test_agent_state_creation() {
    let state = codex_engine::AgentState::new(
        "agent_1".to_string(),
        vec!["memory1".to_string(), "memory2".to_string()]
    );
    
    assert_eq!(state.id, "agent_1");
    assert_eq!(state.memory.len(), 2);
}

#[test]
fn test_agent_state_metrics() {
    let mut state = codex_engine::AgentState::new(
        "agent_1".to_string(),
        vec![]
    );
    
    state.set_metric("score".to_string(), 0.95);
    assert_eq!(state.get_metric("score".to_string()), Some(0.95));
    
    let keys = state.get_metric_keys();
    assert!(keys.contains(&"score".to_string()));
}

#[test]
fn test_serialization_round_trip() {
    let mut state = codex_engine::AgentState::new(
        "agent_1".to_string(),
        vec!["item1".to_string(), "item2".to_string()]
    );
    state.set_metric("accuracy".to_string(), 0.98);
    
    let serialized = codex_engine::serialize_state(&state).unwrap();
    let deserialized = codex_engine::deserialize_state(&serialized).unwrap();
    
    assert_eq!(state.id, deserialized.id);
    assert_eq!(state.memory, deserialized.memory);
    assert_eq!(
        state.get_metric("accuracy".to_string()),
        deserialized.get_metric("accuracy".to_string())
    );
}

#[test]
fn test_serialization_size() {
    let state = codex_engine::AgentState::new(
        "agent_1".to_string(),
        vec!["memory".to_string(); 1000]
    );
    
    let msgpack = codex_engine::serialize_state(&state).unwrap();
    
    // MessagePack should be compact
    // 1000 * 6 bytes ("memory") + overhead should be < 10KB
    assert!(msgpack.len() < 10000, "Serialized size: {} bytes", msgpack.len());
}

#[test]
fn test_serialization_performance() {
    let mut state = codex_engine::AgentState::new(
        "agent_1".to_string(),
        vec!["item".to_string(); 1000]
    );
    
    for i in 0..10 {
        state.set_metric(format!("metric_{}", i), i as f64);
    }
    
    let iterations = 1000;
    
    // Serialize
    let start = Instant::now();
    for _ in 0..iterations {
        let _ = codex_engine::serialize_state(&state).unwrap();
    }
    let serialize_time = start.elapsed();
    
    // Deserialize
    let serialized = codex_engine::serialize_state(&state).unwrap();
    let start = Instant::now();
    for _ in 0..iterations {
        let _ = codex_engine::deserialize_state(&serialized).unwrap();
    }
    let deserialize_time = start.elapsed();
    
    let serialize_per_op = serialize_time.as_micros() / iterations;
    let deserialize_per_op = deserialize_time.as_micros() / iterations;
    
    // Should be fast (< 100µs per operation)
    assert!(serialize_per_op < 100, "Serialize: {}µs", serialize_per_op);
    assert!(deserialize_per_op < 100, "Deserialize: {}µs", deserialize_per_op);
}

#[test]
fn test_large_state_serialization() {
    let state = codex_engine::AgentState::new(
        "agent_1".to_string(),
        vec!["large_memory_item".to_string(); 10000]
    );
    
    let serialized = codex_engine::serialize_state(&state).unwrap();
    let deserialized = codex_engine::deserialize_state(&serialized).unwrap();
    
    assert_eq!(state.memory.len(), deserialized.memory.len());
}

#[test]
fn test_empty_state_serialization() {
    let state = codex_engine::AgentState::new(
        "agent_1".to_string(),
        vec![]
    );
    
    let serialized = codex_engine::serialize_state(&state).unwrap();
    let deserialized = codex_engine::deserialize_state(&serialized).unwrap();
    
    assert_eq!(state.id, deserialized.id);
    assert!(deserialized.memory.is_empty());
}

#[test]
fn test_concurrent_serialization() {
    use std::thread;
    use std::sync::Arc;
    
    let state = Arc::new(codex_engine::AgentState::new(
        "agent_1".to_string(),
        vec!["item".to_string(); 100]
    ));
    
    let handles: Vec<_> = (0..10)
        .map(|_| {
            let state_clone = Arc::clone(&state);
            thread::spawn(move || {
                for _ in 0..100 {
                    let _ = codex_engine::serialize_state(&state_clone).unwrap();
                }
            })
        })
        .collect();
    
    for handle in handles {
        handle.join().unwrap();
    }
}
