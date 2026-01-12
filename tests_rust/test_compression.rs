// Rust integration tests for Compression

use std::time::Instant;

#[test]
fn test_lz4_compression() {
    let pipeline = codex_engine::CompressionPipeline::new("lz4".to_string(), None).unwrap();
    
    let data = b"Hello, World! This is test data.";
    let compressed = pipeline.compress(data).unwrap();
    let decompressed = pipeline.decompress(&compressed).unwrap();
    
    assert_eq!(data, decompressed.as_slice());
}

#[test]
fn test_zstd_compression() {
    let pipeline = codex_engine::CompressionPipeline::new("zstd".to_string(), Some(3)).unwrap();
    
    let data = b"Hello, World! This is test data.";
    let compressed = pipeline.compress(data).unwrap();
    let decompressed = pipeline.decompress(&compressed).unwrap();
    
    assert_eq!(data, decompressed.as_slice());
}

#[test]
fn test_compression_ratio() {
    let pipeline = codex_engine::CompressionPipeline::new("lz4".to_string(), None).unwrap();
    
    // Highly compressible data
    let data = vec![b'x'; 1024 * 100]; // 100KB of 'x'
    let compressed = pipeline.compress(&data).unwrap();
    
    let ratio = data.len() as f64 / compressed.len() as f64;
    
    // Should achieve > 10x compression on repetitive data
    assert!(ratio > 10.0, "Compression ratio: {:.2}x", ratio);
}

#[test]
fn test_lz4_performance() {
    let pipeline = codex_engine::CompressionPipeline::new("lz4".to_string(), None).unwrap();
    
    let data = vec![0u8; 1024 * 1024]; // 1MB
    
    let start = Instant::now();
    let compressed = pipeline.compress(&data).unwrap();
    let compress_time = start.elapsed();
    
    let start = Instant::now();
    let _ = pipeline.decompress(&compressed).unwrap();
    let decompress_time = start.elapsed();
    
    // Should be very fast (< 10ms for 1MB)
    assert!(compress_time.as_millis() < 10, "Compression took {:?}", compress_time);
    assert!(decompress_time.as_millis() < 10, "Decompression took {:?}", decompress_time);
}

#[test]
fn test_zstd_levels() {
    for level in [1, 3, 10] {
        let pipeline = codex_engine::CompressionPipeline::new("zstd".to_string(), Some(level)).unwrap();
        
        let data = b"Test data for compression level testing";
        let compressed = pipeline.compress(data).unwrap();
        let decompressed = pipeline.decompress(&compressed).unwrap();
        
        assert_eq!(data, decompressed.as_slice());
    }
}

#[test]
fn test_large_data_compression() {
    let pipeline = codex_engine::CompressionPipeline::new("lz4".to_string(), None).unwrap();
    
    // 10MB of data
    let data = vec![42u8; 1024 * 1024 * 10];
    
    let compressed = pipeline.compress(&data).unwrap();
    let decompressed = pipeline.decompress(&compressed).unwrap();
    
    assert_eq!(data, decompressed);
}

#[test]
fn test_empty_data() {
    let pipeline = codex_engine::CompressionPipeline::new("lz4".to_string(), None).unwrap();
    
    let data = b"";
    let compressed = pipeline.compress(data).unwrap();
    let decompressed = pipeline.decompress(&compressed).unwrap();
    
    assert_eq!(data, decompressed.as_slice());
}

#[test]
fn test_invalid_codec() {
    let result = codex_engine::CompressionPipeline::new("invalid".to_string(), None);
    assert!(result.is_err());
}

#[test]
fn test_compression_throughput() {
    let pipeline = codex_engine::CompressionPipeline::new("lz4".to_string(), None).unwrap();
    
    let data = vec![0u8; 1024 * 1024]; // 1MB
    let iterations = 100;
    
    let start = Instant::now();
    for _ in 0..iterations {
        let _ = pipeline.compress(&data).unwrap();
    }
    let elapsed = start.elapsed();
    
    let throughput = (iterations * data.len()) as f64 / elapsed.as_secs_f64() / (1024.0 * 1024.0);
    
    // Should achieve > 100 MB/s
    assert!(throughput > 100.0, "Throughput: {:.2} MB/s", throughput);
}
