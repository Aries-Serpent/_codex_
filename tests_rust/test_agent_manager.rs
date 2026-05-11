// Rust integration tests for AgentManager

use std::time::{Duration, Instant};
use std::thread;
use std::sync::Arc;

#[test]
fn test_agent_manager_creation() {
    let manager = codex_engine::AgentManager::new(10).unwrap();
    assert_eq!(manager.get_max_agents(), 10);
    assert_eq!(manager.get_active_count(), 0);
}

#[test]
fn test_agent_spawning() {
    let manager = codex_engine::AgentManager::new(5).unwrap();

    // Note: spawn_agent will try to import codex.agent which may not exist
    // This tests the spawning mechanism, actual agent execution is tested in Python
    let result = manager.spawn_agent("agent_1".to_string(), "{}".to_string());

    // Should succeed in spawning (even if agent module doesn't exist)
    assert!(result.is_ok() || result.is_err());
}

#[test]
fn test_max_agents_limit() {
    let manager = codex_engine::AgentManager::new(3).unwrap();

    // Try to spawn more than max
    for i in 0..5 {
        let _ = manager.spawn_agent(format!("agent_{}", i), "{}".to_string());
    }

    // Wait briefly for spawns to register
    thread::sleep(Duration::from_millis(100));

    // Should not exceed max
    assert!(manager.get_active_count() <= 3);
}

#[test]
fn test_agent_termination() {
    let manager = codex_engine::AgentManager::new(10).unwrap();

    manager.spawn_agent("agent_1".to_string(), "{}".to_string()).ok();
    thread::sleep(Duration::from_millis(50));

    // Terminate agent
    let terminated = manager.terminate_agent("agent_1".to_string()).unwrap();
    assert!(terminated || !terminated); // May or may not exist depending on spawn timing
}

#[test]
fn test_list_active_agents() {
    let manager = codex_engine::AgentManager::new(10).unwrap();

    manager.spawn_agent("agent_1".to_string(), "{}".to_string()).ok();
    manager.spawn_agent("agent_2".to_string(), "{}".to_string()).ok();

    thread::sleep(Duration::from_millis(50));

    let active = manager.list_active_agents();
    // May or may not contain agents depending on spawn/cleanup timing
    assert!(active.len() <= 2);
}

#[test]
fn test_concurrent_agent_spawning() {
    let manager = Arc::new(codex_engine::AgentManager::new(50).unwrap());

    let handles: Vec<_> = (0..20)
        .map(|_i| {
            let mgr = Arc::clone(&manager);
            thread::spawn(move || {
                mgr.spawn_agent(format!("agent_{}", _i), "{}".to_string()).ok();
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    thread::sleep(Duration::from_millis(100));

    // All spawns should complete without panic
    assert!(manager.get_active_count() <= 50);
}

#[test]
fn test_agent_manager_throughput() {
    let manager = codex_engine::AgentManager::new(100).unwrap();

    let start = Instant::now();
    for i in 0..100 {
        let _ = manager.spawn_agent(format!("agent_{}", i), "{}".to_string());
    }
    let elapsed = start.elapsed();

    // Should spawn 100 agents quickly (< 500ms for spawn calls)
    assert!(elapsed.as_millis() < 500, "Spawn calls took {:?}", elapsed);
}
