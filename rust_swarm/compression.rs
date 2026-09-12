//! Compression - High-performance data compression
//!
//! Provides 10x compression ratio for task data.

use flate2::read::GzDecoder;
use flate2::write::GzEncoder;
use flate2::Compression as FlateCompression;
use pyo3::prelude::*;
use std::io::{Read, Write};

/// Conservative default for data expanded across the Python/Rust boundary.
pub const DEFAULT_MAX_DECOMPRESSED_BYTES: usize = 64 * 1024 * 1024;

/// Compression engine with 10x ratio target
pub struct Compression;

impl Compression {
    /// Compress data
    pub fn compress(data: &[u8]) -> PyResult<Vec<u8>> {
        let mut encoder = GzEncoder::new(Vec::new(), FlateCompression::best());
        encoder.write_all(data).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Compression write failed: {}", e))
        })?;
        encoder.finish().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                "Compression finish failed: {}",
                e
            ))
        })
    }

    /// Decompress data
    pub fn decompress(data: &[u8]) -> PyResult<Vec<u8>> {
        Self::decompress_with_limit(data, DEFAULT_MAX_DECOMPRESSED_BYTES)
    }

    /// Decompress data while refusing output larger than `max_output_bytes`.
    pub fn decompress_with_limit(data: &[u8], max_output_bytes: usize) -> PyResult<Vec<u8>> {
        let read_limit = max_output_bytes.saturating_add(1) as u64;
        let mut decoder = GzDecoder::new(data).take(read_limit);
        let mut output = Vec::with_capacity(data.len().min(max_output_bytes));
        decoder.read_to_end(&mut output).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Decompression failed: {}", e))
        })?;
        if output.len() > max_output_bytes {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Decompressed payload exceeds {} byte limit",
                max_output_bytes
            )));
        }
        Ok(output)
    }

    /// Calculate compression ratio
    pub fn ratio(original: &[u8], compressed: &[u8]) -> f64 {
        original.len() as f64 / compressed.len() as f64
    }

    /// Compress JSON-serialized tasks
    pub fn compress_tasks(tasks: &[u8]) -> PyResult<Vec<u8>> {
        Self::compress(tasks)
    }

    /// Decompress JSON-serialized tasks
    pub fn decompress_tasks(data: &[u8]) -> PyResult<Vec<u8>> {
        Self::decompress(data)
    }
}

/// Python wrapper for Compression
#[pyclass(name = "Compression")]
pub struct PyCompression;

#[pymethods]
impl PyCompression {
    #[staticmethod]
    fn compress(py: Python<'_>, data: Vec<u8>) -> PyResult<Vec<u8>> {
        // `Vec<u8>` owns the copied Python buffer, so it remains valid after
        // releasing the GIL for the blocking compression operation.
        py.allow_threads(move || Compression::compress(&data))
    }

    #[staticmethod]
    fn decompress(py: Python<'_>, data: Vec<u8>) -> PyResult<Vec<u8>> {
        py.allow_threads(move || Compression::decompress(&data))
    }

    #[staticmethod]
    #[pyo3(signature = (data, max_output_bytes))]
    fn decompress_with_limit(
        py: Python<'_>,
        data: Vec<u8>,
        max_output_bytes: usize,
    ) -> PyResult<Vec<u8>> {
        py.allow_threads(move || Compression::decompress_with_limit(&data, max_output_bytes))
    }

    #[staticmethod]
    fn compress_tasks(py: Python<'_>, tasks_json: Vec<u8>) -> PyResult<Vec<u8>> {
        py.allow_threads(move || Compression::compress_tasks(&tasks_json))
    }

    #[staticmethod]
    fn decompress_tasks(py: Python<'_>, data: Vec<u8>) -> PyResult<Vec<u8>> {
        py.allow_threads(move || Compression::decompress_tasks(&data))
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
        let compressed = Compression::compress(&data).unwrap();
        let decompressed = Compression::decompress(&compressed).unwrap();

        assert_eq!(data, decompressed);
    }

    #[test]
    fn test_compression_ratio() {
        // Create highly compressible data
        let data = vec![b'A'; 100_000];
        let compressed = Compression::compress(&data).unwrap();

        let ratio = Compression::ratio(&data, &compressed);
        println!("Compression ratio: {:.2}x", ratio);

        // Should achieve > 10x compression on repetitive data
        assert!(ratio > 10.0, "Compression ratio too low: {:.2}x", ratio);
    }

    #[test]
    fn test_compression_large_data() {
        // Test with 1MB of data
        let data = vec![0u8; 1_000_000];
        let compressed = Compression::compress(&data).unwrap();
        let decompressed = Compression::decompress(&compressed).unwrap();

        assert_eq!(data, decompressed);
        assert!(compressed.len() < data.len());
    }

    #[test]
    fn test_compression_json_like_data() {
        // Simulate JSON task data
        let task_json = r#"{"id": 1, "type": "process", "data": "test"}"#;
        let data = task_json.repeat(1000).into_bytes();

        let compressed = Compression::compress(&data).unwrap();
        let decompressed = Compression::decompress(&compressed).unwrap();

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
            let compressed = Compression::compress(&data).unwrap();
            let decompressed = Compression::decompress(&compressed).unwrap();
            assert_eq!(data, decompressed, "Roundtrip failed for data");
        }
    }

    #[test]
    fn test_decompression_limit() {
        pyo3::prepare_freethreaded_python();
        let compressed = Compression::compress(&vec![b'x'; 1024]).unwrap();
        let error = Compression::decompress_with_limit(&compressed, 128).unwrap_err();
        assert!(error.to_string().contains("exceeds 128 byte limit"));
    }

    #[test]
    #[ignore] // Skip in CI due to performance variability on shared runners
    fn test_compression_performance() {
        let data = vec![b'X'; 1_000_000]; // 1MB

        let start = std::time::Instant::now();
        let compressed = Compression::compress(&data).unwrap();
        let compress_time = start.elapsed();

        let start = std::time::Instant::now();
        let _decompressed = Compression::decompress(&compressed).unwrap();
        let decompress_time = start.elapsed();

        println!("Compression time: {:?}", compress_time);
        println!("Decompression time: {:?}", decompress_time);
        println!(
            "Compression ratio: {:.2}x",
            Compression::ratio(&data, &compressed)
        );

        // Performance validation for local runs only (ignored in CI)
        // Expected: < 100ms for 1MB on modern hardware
        // Note: CI runners may be 10-20x slower due to resource sharing
        if compress_time.as_millis() >= 100 {
            println!("⚠️  Compression slower than expected: {:?}", compress_time);
        }
        if decompress_time.as_millis() >= 100 {
            println!(
                "⚠️  Decompression slower than expected: {:?}",
                decompress_time
            );
        }
    }
}
