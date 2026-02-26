// Compression: LZ4/Zstd compression pipeline
//
// High-performance compression middleware for data efficiency

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::io::{BufWriter, Write};

/// Compression codec selection
#[derive(Clone, Copy)]
enum CompressionCodec {
    LZ4,
    Zstd(i32), // compression level
}

/// High-performance compression pipeline
///
/// Provides LZ4 (fast) and Zstd (high ratio) compression for agent data
#[pyclass]
pub struct CompressionPipeline {
    codec: CompressionCodec,
}

#[pymethods]
impl CompressionPipeline {
    /// Create a new compression pipeline
    ///
    /// # Arguments
    /// * `codec` - Compression codec ("lz4" or "zstd")
    /// * `level` - Compression level (for zstd, 1-22; default 3)
    #[new]
    #[pyo3(signature = (codec, level=None))]
    fn new(codec: String, level: Option<i32>) -> PyResult<Self> {
        let codec = match codec.as_str() {
            "lz4" => CompressionCodec::LZ4,
            "zstd" => CompressionCodec::Zstd(level.unwrap_or(3)),
            _ => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid codec: {}. Use 'lz4' or 'zstd'", codec)
            )),
        };
        Ok(CompressionPipeline { codec })
    }

    /// Compress data
    ///
    /// # Arguments
    /// * `data` - Raw bytes to compress
    ///
    /// # Returns
    /// Compressed bytes
    fn compress<'py>(&self, py: Python<'py>, data: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
        let result = match self.codec {
            CompressionCodec::LZ4 => self.compress_lz4(data)?,
            CompressionCodec::Zstd(level) => self.compress_zstd(data, level)?,
        };
        Ok(PyBytes::new_bound(py, &result))
    }

    /// Decompress data
    ///
    /// # Arguments
    /// * `data` - Compressed bytes
    ///
    /// # Returns
    /// Decompressed bytes
    fn decompress<'py>(&self, py: Python<'py>, data: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
        let result = match self.codec {
            CompressionCodec::LZ4 => self.decompress_lz4(data)?,
            CompressionCodec::Zstd(_) => self.decompress_zstd(data)?,
        };
        Ok(PyBytes::new_bound(py, &result))
    }
}

impl CompressionPipeline {
    fn compress_lz4(&self, data: &[u8]) -> PyResult<Vec<u8>> {
        let mut output = Vec::new();
        {
            let mut writer = BufWriter::with_capacity(4096, &mut output);
            let mut encoder = lz4::EncoderBuilder::new()
                .level(4)
                .build(&mut writer)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

            encoder.write_all(data)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

            let (_writer, result) = encoder.finish();
            result.map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        }
        Ok(output)
    }

    fn decompress_lz4(&self, data: &[u8]) -> PyResult<Vec<u8>> {
        let mut decoder = lz4::Decoder::new(data)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

        let mut output = Vec::new();
        std::io::copy(&mut decoder, &mut output)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

        Ok(output)
    }

    fn compress_zstd(&self, data: &[u8], level: i32) -> PyResult<Vec<u8>> {
        zstd::encode_all(data, level)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    fn decompress_zstd(&self, data: &[u8]) -> PyResult<Vec<u8>> {
        zstd::decode_all(data)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }
}
