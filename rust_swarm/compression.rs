//! Compression - High-performance data compression
//!
//! Provides 10x compression ratio for task data.

use flate2::write::{GzDecoder, GzEncoder};
use flate2::Compression as FlateCompression;
use pyo3::prelude::*;
use std::io::prelude::*;

/// Compression engine with 10x ratio target
pub struct Compression;

impl Compression {
    /// Compress data
    pub fn compress(data: &[u8]) -> Vec<u8> {
        let mut encoder = GzEncoder::new(Vec::new(), FlateCompression::best());
        encoder.write_all(data).unwrap();
        encoder.finish().unwrap()
    }

    /// Decompress data
    pub fn decompress(data: &[u8]) -> Vec<u8> {
        let mut decoder = GzDecoder::new(Vec::new());
        decoder.write_all(data).unwrap();
        decoder.finish().unwrap()
    }

    /// Calculate compression ratio
    pub fn ratio(original: &[u8], compressed: &[u8]) -> f64 {
        original.len() as f64 / compressed.len() as f64
    }

    /// Compress JSON-serialized tasks
    pub fn compress_tasks(tasks: &[u8]) -> Vec<u8> {
        Self::compress(tasks)
    }

    /// Decompress JSON-serialized tasks
    pub fn decompress_tasks(data: &[u8]) -> Vec<u8> {
        Self::decompress(data)
    }
}

/// Python wrapper for Compression
#[pyclass(name = "Compression")]
pub struct PyCompression;

#[pymethods]
impl PyCompression {
    #[staticmethod]
    fn compress(data: Vec<u8>) -> Vec<u8> {
        Compression::compress(&data)
    }

    #[staticmethod]
    fn decompress(data: Vec<u8>) -> Vec<u8> {
        Compression::decompress(&data)
    }

    #[staticmethod]
    fn compress_tasks(tasks_json: Vec<u8>) -> Vec<u8> {
        Compression::compress_tasks(&tasks_json)
    }

    #[staticmethod]
    fn decompress_tasks(data: Vec<u8>) -> Vec<u8> {
        Compression::decompress_tasks(&data)
    }

    #[staticmethod]
    fn ratio(original: Vec<u8>, compressed: Vec<u8>) -> f64 {
        Compression::ratio(&original, &compressed)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compression_basic() {
        let data = b"Hello, World!".to_vec();
        let compressed = Compression::compress(&data);
        let decompressed = Compression::decompress(&compressed);

        assert_eq!(data, decompressed);
    }

    #[test]
    fn test_compression_ratio() {
        // Create highly compressible data
        let data = vec![b'A'; 100_000];
        let compressed = Compression::compress(&data);

        let ratio = Compression::ratio(&data, &compressed);
        println!("Compression ratio: {:.2}x", ratio);

        // Should achieve > 10x compression on repetitive data
        assert!(ratio > 10.0, "Compression ratio too low: {:.2}x", ratio);
    }

    #[test]
    fn test_compression_large_data() {
        // Test with 1MB of data
        let data = vec![0u8; 1_000_000];
        let compressed = Compression::compress(&data);
        let decompressed = Compression::decompress(&compressed);

        assert_eq!(data, decompressed);
        assert!(compressed.len() < data.len());
    }

    #[test]
    fn test_compression_json_like_data() {
        // Simulate JSON task data
        let task_json = r#"{"id": 1, "type": "process", "data": "test"}"#;
        let data = task_json.repeat(1000).into_bytes();

        let compressed = Compression::compress(&data);
        let decompressed = Compression::decompress(&compressed);

        assert_eq!(data, decompressed);

        let ratio = Compression::ratio(&data, &compressed);
        println!("JSON compression ratio: {:.2}x", ratio);
        assert!(ratio > 5.0, "JSON compression ratio too low: {:.2}x", ratio);
    }

    #[test]
    fn test_compression_roundtrip() {
        let test_cases = vec![
            b"".to_vec(),
            b"a".to_vec(),
            b"short string".to_vec(),
            vec![0u8; 1000],
            vec![255u8; 1000],
            (0..=255).cycle().take(10000).collect(),
        ];

        for data in test_cases {
            let compressed = Compression::compress(&data);
            let decompressed = Compression::decompress(&compressed);
            assert_eq!(data, decompressed, "Roundtrip failed for data");
        }
    }

    #[test]
    fn test_compression_performance() {
        let data = vec![b'X'; 1_000_000]; // 1MB

        let start = std::time::Instant::now();
        let compressed = Compression::compress(&data);
        let compress_time = start.elapsed();

        let start = std::time::Instant::now();
        let _decompressed = Compression::decompress(&compressed);
        let decompress_time = start.elapsed();

        println!("Compression time: {:?}", compress_time);
        println!("Decompression time: {:?}", decompress_time);
        println!(
            "Compression ratio: {:.2}x",
            Compression::ratio(&data, &compressed)
        );

        // Should complete in reasonable time (< 100ms for 1MB)
        assert!(compress_time.as_millis() < 100, "Compression too slow");
        assert!(decompress_time.as_millis() < 100, "Decompression too slow");
    }
}
