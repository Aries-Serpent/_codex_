// Rust integration tests for Orchestrator (Tokio Runtime)
//
// These tests validate the async orchestration layer and Tokio integration

use std::time::Duration;
use tokio::time::sleep;

#[tokio::test]
async fn test_orchestrator_startup() {
    let state = codex_engine::SwarmState::new();
    let orch = codex_engine::Orchestrator::new(state).unwrap();
    
    assert!(!orch.is_running());
    
    orch.start().unwrap();
    assert!(orch.is_running());
    
    // Let it run briefly
    sleep(Duration::from_millis(500)).await;
    
    orch.stop().unwrap();
}

#[tokio::test]
async fn test_orchestrator_with_agents() {
    let state = codex_engine::SwarmState::new();
    
    // Register some agents
    state.register_agent("agent_1".to_string()).unwrap();
    state.register_agent("agent_2".to_string()).unwrap();
    state.register_agent("agent_3".to_string()).unwrap();
    
    let orch = codex_engine::Orchestrator::new(state.clone()).unwrap();
    orch.start().unwrap();
    
    // Let orchestrator run
    sleep(Duration::from_millis(300)).await;
    
    assert_eq!(state.get_agent_count(), 3);
    
    orch.stop().unwrap();
}

#[tokio::test]
async fn test_orchestrator_lifecycle() {
    let state = codex_engine::SwarmState::new();
    let orch = codex_engine::Orchestrator::new(state).unwrap();
    
    // Start and stop multiple times
    for _ in 0..5 {
        orch.start().unwrap();
        assert!(orch.is_running());
        
        sleep(Duration::from_millis(100)).await;
        
        orch.stop().unwrap();
    }
}

#[tokio::test]
async fn test_orchestrator_heartbeat() {
    let state = codex_engine::SwarmState::new();
    
    // Register agents
    for i in 0..10 {
        state.register_agent(format!("agent_{}", i)).unwrap();
    }
    
    let orch = codex_engine::Orchestrator::new(state.clone()).unwrap();
    orch.start().unwrap();
    
    // Let orchestrator run for multiple heartbeat cycles (100ms interval)
    sleep(Duration::from_millis(500)).await;
    
    // Verify state is maintained
    assert_eq!(state.get_agent_count(), 10);
    
    orch.stop().unwrap();
}
