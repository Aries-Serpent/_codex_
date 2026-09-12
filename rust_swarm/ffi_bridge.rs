//! FFI Bridge - Safe Python interop layer
//!
//! Provides safe FFI boundaries between Rust and Python.

use parking_lot::RwLock;
use pyo3::prelude::*;
use pyo3::types::PyString;
use std::sync::Arc;

pub const MAX_MESSAGEPACK_VALUE_BYTES: usize = 16 * 1024 * 1024;
pub const MAX_MESSAGEPACK_BYTES: usize = MAX_MESSAGEPACK_VALUE_BYTES + 5;

fn msgpack_string_length(data: &[u8]) -> Result<(usize, usize), String> {
    let Some(&marker) = data.first() else {
        return Err("MessagePack payload is empty".to_string());
    };
    match marker {
        0xa0..=0xbf => Ok((1, (marker & 0x1f) as usize)),
        0xd9 if data.len() >= 2 => Ok((2, data[1] as usize)),
        0xda if data.len() >= 3 => Ok((3, u16::from_be_bytes([data[1], data[2]]) as usize)),
        0xdb if data.len() >= 5 => Ok((
            5,
            u32::from_be_bytes([data[1], data[2], data[3], data[4]]) as usize,
        )),
        _ => Err("MessagePack bridge payload must contain one string".to_string()),
    }
}

/// FFI bridge for safe Python-Rust communication
pub struct FFIBridge {
    message_count: Arc<RwLock<u64>>,
    error_count: Arc<RwLock<u64>>,
}

impl FFIBridge {
    /// Create new FFI bridge
    pub fn new() -> Self {
        Self {
            message_count: Arc::new(RwLock::new(0)),
            error_count: Arc::new(RwLock::new(0)),
        }
    }

    fn value_error(&self, message: String) -> PyErr {
        *self.error_count.write() += 1;
        PyErr::new::<pyo3::exceptions::PyValueError, _>(message)
    }

    /// Convert Python object to Rust bytes
    pub fn from_python(&self, py_obj: &Bound<'_, PyAny>) -> Result<Vec<u8>, String> {
        *self.message_count.write() += 1;
        let value = py_obj.extract::<String>().map_err(|_| {
            *self.error_count.write() += 1;
            "FFI bridge currently accepts strings only".to_string()
        })?;
        if value.len() > MAX_MESSAGEPACK_VALUE_BYTES {
            *self.error_count.write() += 1;
            return Err(format!(
                "MessagePack value exceeds {} byte limit",
                MAX_MESSAGEPACK_VALUE_BYTES
            ));
        }
        rmp_serde::to_vec(&value).map_err(|error| {
            *self.error_count.write() += 1;
            format!("MessagePack encoding failed: {error}")
        })
    }

    /// Convert Rust bytes to Python object
    pub fn to_python(&self, data: &[u8], py: Python<'_>) -> PyResult<PyObject> {
        *self.message_count.write() += 1;
        if data.len() > MAX_MESSAGEPACK_BYTES {
            return Err(self.value_error(format!(
                "MessagePack payload exceeds {} byte limit",
                MAX_MESSAGEPACK_BYTES
            )));
        }
        let (header_len, decoded_len) =
            msgpack_string_length(data).map_err(|message| self.value_error(message))?;
        if decoded_len > MAX_MESSAGEPACK_VALUE_BYTES
            || header_len.checked_add(decoded_len) != Some(data.len())
        {
            return Err(self.value_error(
                "MessagePack string length is invalid or exceeds the decoded limit".to_string(),
            ));
        }
        let value: String = rmp_serde::from_slice(data)
            .map_err(|error| self.value_error(format!("MessagePack decoding failed: {error}")))?;
        Ok(PyString::new(py, &value).into_any().unbind())
    }

    /// Get message count
    pub fn message_count(&self) -> u64 {
        *self.message_count.read()
    }

    /// Get error count
    pub fn error_count(&self) -> u64 {
        *self.error_count.read()
    }
}

impl Default for FFIBridge {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ffi_bridge_creation() {
        let bridge = FFIBridge::new();
        assert_eq!(bridge.message_count(), 0);
        assert_eq!(bridge.error_count(), 0);
    }

    #[test]
    fn test_ffi_message_counting() {
        let bridge = FFIBridge::new();

        // Directly increment message count for testing
        for _ in 0..100 {
            *bridge.message_count.write() += 1;
        }

        assert_eq!(bridge.message_count(), 100);
    }

    #[test]
    fn test_ffi_thread_safety() {
        use std::thread;

        let bridge = Arc::new(FFIBridge::new());
        let mut handles = vec![];

        for _ in 0..10 {
            let bridge = Arc::clone(&bridge);
            let handle = thread::spawn(move || {
                for _ in 0..100 {
                    *bridge.message_count.write() += 1;
                }
            });
            handles.push(handle);
        }

        for handle in handles {
            handle.join().unwrap();
        }

        assert_eq!(bridge.message_count(), 1000);
    }

    #[test]
    fn test_msgpack_length_validation_rejects_oversized_declaration() {
        let payload = [0xdb, 0xff, 0xff, 0xff, 0xff];
        let (_, decoded_len) = msgpack_string_length(&payload).unwrap();
        assert!(decoded_len > MAX_MESSAGEPACK_VALUE_BYTES);
    }

    #[test]
    fn test_msgpack_string_roundtrip_shape() {
        let encoded = rmp_serde::to_vec(&"experimental").unwrap();
        let (header_len, decoded_len) = msgpack_string_length(&encoded).unwrap();
        assert_eq!(header_len + decoded_len, encoded.len());
        let decoded: String = rmp_serde::from_slice(&encoded).unwrap();
        assert_eq!(decoded, "experimental");
    }
}
