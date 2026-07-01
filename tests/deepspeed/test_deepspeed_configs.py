#         assert config["train_batch_size"] == (, "Condition must be true"
#             config["train_micro_batch_size_per_gpu"] * config["gradient_accumulation_steps"]
#         )
# - ZeRO stage configurations
# - Optimizer state partitioning
# - Gradient checkpointing
# - Mixed precision configurations
#     def test_validate_memory_config(self):
# """
#         assert config["train_batch_size"] == (, "Condition must be true"
#             config["train_micro_batch_size_per_gpu"] * config["gradient_accumulation_steps"]
#         )
# class TestDeepSpeedZeROStages:
# class TestDeepSpeedZeROStages:
#     """Test ZeRO stage configurations"""
#     def test_zero_stage_0_config(self):
#     def test_zero_stage_0_config(self):
#         """Test ZeRO Stage 0 (disabled) configuration"""
#         config = {
#             "zero_optimization": {
#                 "stage": 0,
#             }
#         }
#         assert config["zero_optimization"]["stage"] == 0, "Condition must be true"
#         # Stage 0 = no optimization, baseline
# 
#     def test_zero_stage_1_config(self):
#     def test_zero_stage_1_config(self):
#         """Test ZeRO Stage 1 (optimizer state partitioning) configuration"""
#         config = {
#             "zero_optimization": {
#                 "stage": 1,
#                 "reduce_bucket_size": 5e8,
#                 "allgather_bucket_size": 5e8,
#             }
#         }
#         assert config["zero_optimization"]["stage"] == 1, "Condition must be true"
#         assert "reduce_bucket_size" in config["zero_optimization"], "Condition must be true"
#         assert "allgather_bucket_size" in config["zero_optimization"], "Condition must be true"
# 
#     def test_zero_stage_2_config(self):
#     def test_zero_stage_2_config(self):
#         """Test ZeRO Stage 2 (optimizer + gradient state partitioning) configuration"""
#         config = {
#             "zero_optimization": {
#                 "stage": 2,
#                 "contiguous_gradients": True,
#                 "overlap_comm": True,
#                 "reduce_scatter": True,
#                 "reduce_bucket_size": 5e8,
#                 "allgather_bucket_size": 5e8,
#             }
#         }
#         assert config["zero_optimization"]["stage"] == 2, "Condition must be true"
#         assert config["zero_optimization"]["contiguous_gradients"] is True, "Condition must be true"
#         assert config["zero_optimization"]["overlap_comm"] is True, "Condition must be true"
# 
#     def test_zero_stage_3_config(self):
#     def test_zero_stage_3_config(self):
#         """Test ZeRO Stage 3 (full parameter partitioning) configuration"""
#         config = {
#             "zero_optimization": {
#                 "stage": 3,
#                 "stage3_prefetch_bucket_size": 5e8,
#                 "stage3_param_persistence_threshold": 1e6,
#                 "stage3_max_live_parameters": 1e9,
#                 "stage3_max_reuse_distance": 1e9,
#                 "contiguous_gradients": True,
#                 "overlap_comm": True,
#             }
#         }
#         assert config["zero_optimization"]["stage"] == 3, "Condition must be true"
#         assert "stage3_prefetch_bucket_size" in config["zero_optimization"], "Condition must be true"
#         assert "stage3_param_persistence_threshold" in config["zero_optimization"], "Condition must be true"
# 
#     def test_invalid_zero_stage(self):
#     def test_invalid_zero_stage(self):
#         """Test invalid ZeRO stage raises appropriate error"""
#         config = {
#             "zero_optimization": {
#                 "stage": 4,  # Invalid stage
#             }
#         }
#         stage = config["zero_optimization"]["stage"]
#         assert stage not in [0, 1, 2, 3], "Stage 4 is invalid"
# 
#         # Validate relationship
#         assert config["train_batch_size"] == (, "Condition must be true"
#             config["train_micro_batch_size_per_gpu"] * config["gradient_accumulation_steps"]
#         )
# 
#     def test_optimizer_state_cpu_offload(self):
#     def test_optimizer_state_cpu_offload(self):
#         """Test CPU offloading of optimizer states"""
#         config = {
#             "zero_optimization": {
#                 "stage": 2,
#                 "offload_optimizer": {
#                     "device": "cpu",
#                     "pin_memory": True,
#                 },
#             }
#         }
#         assert config["zero_optimization"]["offload_optimizer"]["device"] == "cpu", "Condition must be true"
#         assert config["zero_optimization"]["offload_optimizer"]["pin_memory"] is True, "Condition must be true"
# 
#     def test_optimizer_state_nvme_offload(self):
#     def test_optimizer_state_nvme_offload(self):
#         """Test NVMe offloading of optimizer states"""
#         config = {
#             "zero_optimization": {
#                 "stage": 3,
#                 "offload_optimizer": {
#                     "device": "nvme",
#                     "nvme_path": "/local_nvme",
#                     "pin_memory": True,
#                 },
#             }
#         }
#         assert config["zero_optimization"]["offload_optimizer"]["device"] == "nvme", "Condition must be true"
#         assert "nvme_path" in config["zero_optimization"]["offload_optimizer"], "Condition must be true"
# 
#     def test_parameter_offload(self):
#     def test_parameter_offload(self):
#         """Test parameter offloading (ZeRO Stage 3)"""
#         config = {
#             "zero_optimization": {
#                 "stage": 3,
#                 "offload_param": {
#                     "device": "cpu",
#                     "pin_memory": True,
#                 },
#             }
#         }
#         assert config["zero_optimization"]["offload_param"]["device"] == "cpu", "Condition must be true"
# 
#     def test_optimizer_states_config(self):
#     def test_optimizer_states_config(self):
#         """Test optimizer state management"""
#         config = {
#             "zero_optimization": {
#                 "stage": 1,
#                 "reduce_bucket_size": 5e8,
#                 "allgather_bucket_size": 5e8,
#             }
#         }
#         assert config["zero_optimization"]["reduce_bucket_size"] > 0, "Value must be greater than zero"
#         assert config["zero_optimization"]["allgather_bucket_size"] > 0, "Value must be greater than zero"
# 
#         # Validate relationship
#         assert config["train_batch_size"] == (, "Condition must be true"
#             config["train_micro_batch_size_per_gpu"] * config["gradient_accumulation_steps"]
#         )
# 
#     def test_activation_checkpointing_enabled(self):
#     def test_activation_checkpointing_enabled(self):
#         """Test activation checkpointing configuration"""
#         config = {
#             "activation_checkpointing": {
#                 "partition_activations": True,
#                 "cpu_checkpointing": False,
#                 "contiguous_memory_optimization": True,
#                 "number_checkpoints": 4,
#             }
#         }
#         assert config["activation_checkpointing"]["partition_activations"] is True, "Condition must be true"
#         assert config["activation_checkpointing"]["contiguous_memory_optimization"] is True, "Condition must be true"
#         assert config["activation_checkpointing"]["number_checkpoints"] == 4, "Condition must be true"
# 
#     def test_cpu_checkpointing(self):
#     def test_cpu_checkpointing(self):
#         """Test CPU-based activation checkpointing"""
#         config = {
#             "activation_checkpointing": {
#                 "partition_activations": True,
#                 "cpu_checkpointing": True,
#                 "synchronize_checkpoint_boundary": True,
#             }
#         }
#         assert config["activation_checkpointing"]["cpu_checkpointing"] is True, "Condition must be true"
# 
#     def test_gradient_checkpointing_config(self):
#     def test_gradient_checkpointing_config(self):
#         """Test gradient checkpointing parameters"""
#         config = {
#             "gradient_accumulation_steps": 8,
#             "gradient_clipping": 1.0,
#         }
#         assert config["gradient_accumulation_steps"] > 0, "Value must be greater than zero"
#         assert config["gradient_clipping"] > 0, "Value must be greater than zero"
# 
#     def test_activation_memory_optimization(self):
#     def test_activation_memory_optimization(self):
#         """Test activation memory optimization settings"""
#         config = {
#             "activation_checkpointing": {
#                 "partition_activations": True,
#                 "contiguous_memory_optimization": True,
#                 "synchronize_checkpoint_boundary": False,
#             }
#         }
#         assert config["activation_checkpointing"]["partition_activations"] is True, "Condition must be true"
# 
#         # Validate relationship
#         assert config["train_batch_size"] == (, "Condition must be true"
#             config["train_micro_batch_size_per_gpu"] * config["gradient_accumulation_steps"]
#         )
# 
#     def test_fp16_config(self):
#     def test_fp16_config(self):
#         """Test FP16 mixed precision configuration"""
#         config = {
#             "fp16": {
#                 "enabled": True,
#                 "loss_scale": 0,
#                 "initial_scale_power": 16,
#                 "loss_scale_window": 1000,
#                 "hysteresis": 2,
#                 "min_loss_scale": 1,
#             }
#         }
#         assert config["fp16"]["enabled"] is True, "Condition must be true"
#         assert config["fp16"]["loss_scale"] == 0, "Condition must be true"
#         assert config["fp16"]["initial_scale_power"] == 16, "Condition must be true"
# 
#     def test_bf16_config(self):
#     def test_bf16_config(self):
#         """Test BF16 mixed precision configuration"""
#         config = {
#             "bf16": {
#                 "enabled": True,
#             }
#         }
#         assert config["bf16"]["enabled"] is True, "Condition must be true"
# 
#     def test_amp_config(self):
#     def test_amp_config(self):
#         """Test automatic mixed precision configuration"""
#         config = {
#             "amp": {
#                 "enabled": True,
#                 "opt_level": "O1",
#             }
#         }
#         assert config["amp"]["enabled"] is True, "Condition must be true"
#         assert config["amp"]["opt_level"] in ["O0", "O1", "O2", "O3"]
# 
#     def test_mixed_precision_exclusions(self):
#     def test_mixed_precision_exclusions(self):
#         """Test mixed precision with layer exclusions"""
#         config = {
#             "fp16": {
#                 "enabled": True,
#                 "loss_scale": 0,
#             },
#             "amp": {
#                 "enabled": False,  # Cannot enable both FP16 and AMP
#             },
#         }
#         assert not (config["fp16"]["enabled"] and config["amp"]["enabled"]), "Condition must be true"
# 
#         # Validate relationship
#         assert config["train_batch_size"] == (, "Condition must be true"
#             config["train_micro_batch_size_per_gpu"] * config["gradient_accumulation_steps"]
#         )
# 
#     def test_complete_deepspeed_config(self):
#     def test_complete_deepspeed_config(self):
#         """Test complete DeepSpeed configuration"""
#         config = {
#             "train_batch_size": 32,
#             "train_micro_batch_size_per_gpu": 4,
#             "gradient_accumulation_steps": 8,
#             "steps_per_print": 100,
#             "optimizer": {
#                 "type": "AdamW",
#                 "params": {
#                     "lr": 3e-5,
#                     "betas": [0.9, 0.999],
#                     "eps": 1e-8,
#                     "weight_decay": 0.01,
#                 },
#             },
#             "scheduler": {
#                 "type": "WarmupDecayLR",
#                 "params": {
#                     "warmup_min_lr": 0,
#                     "warmup_max_lr": 3e-5,
#                     "warmup_num_steps": 500,
#                     "total_num_steps": 10000,
#                 },
#             },
#             "fp16": {
#                 "enabled": True,
#                 "loss_scale": 0,
#             },
#             "zero_optimization": {
#                 "stage": 2,
#                 "offload_optimizer": {
#                     "device": "cpu",
#                 },
#             },
#         }
#         assert "train_batch_size" in config, "Condition must be true"
#         assert "optimizer" in config, "Condition must be true"
#         assert "scheduler" in config, "Condition must be true"
#         assert "zero_optimization" in config, "Condition must be true"
# 
#         # Validate batch size calculations
#         batch_size = config["train_batch_size"]
#         micro_batch = config["train_micro_batch_size_per_gpu"]
#         grad_accum = config["gradient_accumulation_steps"]
#         # Should satisfy: train_batch_size = micro_batch * grad_accum * world_size
#         # For single GPU: batch_size = micro_batch * grad_accum
#         assert batch_size == micro_batch * grad_accum, "batch_size is not valid"
#         # For single GPU: batch_size = micro_batch * grad_accum
#         assert batch_size == micro_batch * grad_accum, "batch_size is not valid"
# 
#     def test_config_validation_batch_sizes(self):
#     def test_config_validation_batch_sizes(self):
#         """Test batch size configuration validation"""
#         config = {
#             "train_batch_size": 64,
#             "train_micro_batch_size_per_gpu": 4,
#             "gradient_accumulation_steps": 16,
#         }
#         assert config["train_batch_size"] == (, "Condition must be true"
#             config["train_micro_batch_size_per_gpu"] * config["gradient_accumulation_steps"]
#         )
#         )
# 
#     def test_config_with_all_stages(self):
#     def test_config_with_all_stages(self):
#         """Test configurations for all ZeRO stages"""
#         stages = [0, 1, 2, 3]
#         for stage in stages:
#             config = {
#             config = {
#                 "zero_optimization": {
#                     "stage": stage,
#                 }
#             }
#             assert config["zero_optimization"]["stage"] in stages, "Condition must be true"
# 
#     def test_optimizer_config_validation(self):
#     def test_optimizer_config_validation(self):
#         """Test optimizer configuration validation"""
#         valid_optimizers = ["Adam", "AdamW", "SGD", "Lamb"]
#         for opt_type in valid_optimizers:
#             config = {
#             config = {
#                 "optimizer": {
#                     "type": opt_type,
#                     "params": {
#                         "lr": 1e-4,
#                     },
#                 }
#             }
#             assert config["optimizer"]["type"] in valid_optimizers, "Condition must be true"
#             assert "lr" in config["optimizer"]["params"], "Condition must be true"
# 
#     def test_scheduler_config_validation(self):
#     def test_scheduler_config_validation(self):
#         """Test learning rate scheduler configuration"""
#         config = {
#             "scheduler": {
#                 "type": "WarmupDecayLR",
#                 "params": {
#                     "warmup_num_steps": 1000,
#                     "total_num_steps": 10000,
#                 },
#             }
#         }
#         assert config["scheduler"]["type"] == "WarmupDecayLR", "Condition must be true"
#         assert config["scheduler"]["params"]["warmup_num_steps"] > 0, "Value must be greater than zero"
#         assert config["scheduler"]["params"]["total_num_steps"] > 0, "Value must be greater than zero"
#         assert (config["scheduler"]["params"]["warmup_num_steps"], "Condition must be true"
#             < config["scheduler"]["params"]["total_num_steps"]
#         )


class TestDeepSpeedConfigFiles:
    """Test loading and validating DeepSpeed config files"""

    def test_config_json_structure(self, tmp_path):
        """Test creating and loading DeepSpeed JSON config"""
        config = {
            "train_batch_size": 32,
            "fp16": {"enabled": True},
            "zero_optimization": {"stage": 2},
        }

        config_file = tmp_path / "ds_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f)

        # Load and validate
        with open(config_file, "r") as f:
            loaded_config = json.load(f)

        assert loaded_config == config, "loaded_config is not valid"

    def test_config_minimal_valid(self):
        """Test minimal valid DeepSpeed configuration"""
        config = {
            "train_batch_size": 16,
        }

        # Minimal config should have at least train_batch_size
        assert "train_batch_size" in config, "Condition must be true"
        assert config["train_batch_size"] > 0, "Value must be greater than zero"

    def test_config_with_all_features(self):
        """Test configuration with all major features"""
        config = {
            "train_batch_size": 64,
            "train_micro_batch_size_per_gpu": 2,
            "gradient_accumulation_steps": 32,
            "optimizer": {"type": "AdamW", "params": {"lr": 1e-4}},
            "scheduler": {"type": "WarmupDecayLR", "params": {"total_num_steps": 10000}},
            "fp16": {"enabled": True},
            "bf16": {"enabled": False},
            "zero_optimization": {
                "stage": 3,
                "offload_optimizer": {"device": "cpu"},
                "offload_param": {"device": "cpu"},
            },
            "activation_checkpointing": {
                "partition_activations": True,
                "cpu_checkpointing": True,
            },
            "gradient_clipping": 1.0,
            "steps_per_print": 100,
            "wall_clock_breakdown": False,
        }

        # Validate all major sections present
        assert "optimizer" in config, "Condition must be true"
        assert "scheduler" in config, "Condition must be true"
        assert "fp16" in config or "bf16" in config, "Condition must be true"
        assert "zero_optimization" in config, "Condition must be true"
        assert "activation_checkpointing" in config, "Condition must be true"


class TestConfigValidation:
    """Test configuration validation logic"""

    def test_validate_stage_params(self):
        """Test stage-specific parameter validation"""
        # Stage 3 requires stage3_* parameters
        config = {
            "zero_optimization": {
                "stage": 3,
                "stage3_prefetch_bucket_size": 5e8,
                "stage3_param_persistence_threshold": 1e6,
            }
        }

        if config["zero_optimization"]["stage"] == 3:
            assert "stage3_prefetch_bucket_size" in config["zero_optimization"], "Condition must be true"

    def test_validate_offload_requirements(self):
        """Test offload configuration requirements"""
        config = {
            "zero_optimization": {
                "stage": 2,
                "offload_optimizer": {
                    "device": "cpu",
                    "pin_memory": True,
                },
            }
        }

        # Validate offload config structure
        if "offload_optimizer" in config["zero_optimization"]:
            assert "device" in config["zero_optimization"]["offload_optimizer"], "Condition must be true"

    def test_validate_precision_config(self):
        """Test precision configuration validation"""
        config = {
            "fp16": {"enabled": True},
            "bf16": {"enabled": False},
        }

        # Only one precision mode should be enabled
        enabled_count = sum(
            [
                config.get("fp16", {}).get("enabled", False),
                config.get("bf16", {}).get("enabled", False),
            ]
        )

        assert enabled_count <= 1, "Only one precision mode should be enabled"

    def test_validate_memory_config(self):
        """Test memory-related configuration validation"""
        config = {
            "zero_optimization": {
                "stage": 3,
                "stage3_max_live_parameters": 1e9,
                "stage3_max_reuse_distance": 1e9,
            }
        }

        # Memory parameters should be positive
        if "stage3_max_live_parameters" in config["zero_optimization"]:
            assert config["zero_optimization"]["stage3_max_live_parameters"] > 0, "Value must be greater than zero"
