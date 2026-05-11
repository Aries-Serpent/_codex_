// Rust integration tests for SwarmState
//
// These tests validate concurrent access patterns and thread safety
// of the SwarmState implementation using the built codex_engine library.

use std::thread;
use std::sync::Arc;
use std::time::Duration;

#[test]
fn test_swarm_state_creation() {
    let state = codex_engine::SwarmState::new();
    assert_eq!(state.get_agent_count(), 0);
}

#[test]
fn test_single_agent_registration() {
    let state = codex_engine::SwarmState::new();
    state.register_agent("agent_1".to_string()).unwrap();
    assert_eq!(state.get_agent_count(), 1);

    let agents = state.list_agents();
    assert!(agents.contains(&"agent_1".to_string()));
}

#[test]
fn test_agent_status_transitions() {
    let state = codex_engine::SwarmState::new();
    state.register_agent("agent_1".to_string()).unwrap();

    // Test idle state
    let (status, _) = state.get_agent_status("agent_1".to_string()).unwrap();
    assert_eq!(status, "idle");

    // Test working state
    state.set_agent_status("agent_1".to_string(), "working".to_string(), Some("Processing task".to_string())).unwrap();
    let (status, message) = state.get_agent_status("agent_1".to_string()).unwrap();
    assert_eq!(status, "working");
    assert_eq!(message, "Processing task");

    // Test complete state
    state.set_agent_status("agent_1".to_string(), "complete".to_string(), None).unwrap();
    let (status, _) = state.get_agent_status("agent_1".to_string()).unwrap();
    assert_eq!(status, "complete");
}

#[test]
fn test_concurrent_agent_registration() {
    // This is the main test requested in Milestone 1.2
    let state = Arc::new(codex_engine::SwarmState::new());
    let num_threads = 10;
    let agents_per_thread = 10;

    let handles: Vec<_> = (0..num_threads)
        .map(|_thread_id| {
            let state_clone = Arc::clone(&state);
            thread::spawn(move || {
                for i in 0..agents_per_thread {
                    let agent_id = format!("agent_{}_{}", _thread_id, i);
                    state_clone.register_agent(agent_id).unwrap();
                }
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    assert_eq!(state.get_agent_count(), num_threads * agents_per_thread);
}

#[test]
fn test_high_volume_registration() {
    // Test scaling to 1000 agents as mentioned in acceptance criteria
    let state = Arc::new(codex_engine::SwarmState::new());
    let num_agents = 1000;

    let handles: Vec<_> = (0..num_agents)
        .map(|_i| {
            let state_clone = Arc::clone(&state);
            thread::spawn(move || {
                let agent_id = format!("agent_{}", _i);
                state_clone.register_agent(agent_id).unwrap();
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    assert_eq!(state.get_agent_count(), num_agents);
}

#[test]
fn test_concurrent_status_updates() {
    let state = Arc::new(codex_engine::SwarmState::new());

    // Pre-register agents
    for i in 0..100 {
        state.register_agent(format!("agent_{}", i)).unwrap();
    }

    let handles: Vec<_> = (0..100)
        .map(|_i| {
            let state_clone = Arc::clone(&state);
            thread::spawn(move || {
                let agent_id = format!("agent_{}", _i);
                state_clone.set_agent_status(
                    agent_id.clone(),
                    "working".to_string(),
                    Some(format!("Task {}", i))
                ).unwrap();

                // Verify we can read it back
                let (status, _) = state_clone.get_agent_status(agent_id).unwrap();
                assert_eq!(status, "working");
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    assert_eq!(state.get_agent_count(), 100);
}

#[test]
fn test_no_data_races() {
    // Test for data races with concurrent reads and writes
    let state = Arc::new(codex_engine::SwarmState::new());

    // Register initial agents
    for i in 0..50 {
        state.register_agent(format!("agent_{}", i)).unwrap();
    }

    let mut handles = vec![];

    // Writers
    for i in 0..50 {
        let state_clone = Arc::clone(&state);
        let handle = thread::spawn(move || {
            for _ in 0..10 {
                state_clone.set_agent_status(
                    format!("agent_{}", i),
                    "working".to_string(),
                    Some("test".to_string())
                ).unwrap();
                thread::sleep(Duration::from_micros(10));
            }
        });
        handles.push(handle);
    }

    // Readers
    for _ in 0..20 {
        let state_clone = Arc::clone(&state);
        let handle = thread::spawn(move || {
            for i in 0..50 {
                let _ = state_clone.get_agent_status(format!("agent_{}", i % 50));
                thread::sleep(Duration::from_micros(10));
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    assert_eq!(state.get_agent_count(), 50);
}
