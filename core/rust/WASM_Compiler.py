#!/usr/bin/env python3
"""
AI-NEXUS WebAssembly Compiler
Compile Rust modules to WASM for browser execution
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List

class WASMCompiler:
    """Compile Rust code to WebAssembly for high-performance browser execution"""
    
    def __init__(self, rust_project_path: str):
        self.rust_project_path = Path(rust_project_path)
        self.wasm_target = "wasm32-unknown-unknown"
        self.optimization_level = "s"  # Optimize for size
        
    def setup_wasm_toolchain(self):
        """Setup Rust WASM toolchain"""
        print("Setting up WASM toolchain...")
        
        # Add WASM target
        subprocess.run([
            "rustup", "target", "add", self.wasm_target
        ], check=True)
        
        # Install wasm-bindgen for JS interoperability
        subprocess.run([
            "cargo", "install", "wasm-bindgen-cli"
        ], check=True)
        
        print("WASM toolchain setup complete")
    
    def compile_to_wasm(self, crate_name: str, output_dir: str) -> Dict:
        """Compile Rust crate to WebAssembly"""
        print(f"Compiling {crate_name} to WASM...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Build with Cargo
        build_result = subprocess.run([
            "cargo", "build",
            "--target", self.wasm_target,
            "--release",
            "--manifest-path", str(self.rust_project_path / "Cargo.toml")
        ], capture_output=True, text=True)
        
        if build_result.returncode != 0:
            return {
                "success": False,
                "error": build_result.stderr
            }
        
        # Use wasm-bindgen to generate JS bindings
        wasm_file = self.rust_project_path / "target" / self.wasm_target / "release" / f"{crate_name}.wasm"
        
        bindgen_result = subprocess.run([
            "wasm-bindgen",
            "--target", "web",
            "--out-dir", str(output_path),
            str(wasm_file)
        ], capture_output=True, text=True)
        
        if bindgen_result.returncode != 0:
            return {
                "success": False,
                "error": bindgen_result.stderr
            }
        
        # Optimize WASM file
        optimized_wasm = output_path / f"{crate_name}_bg.wasm"
        
        optimize_result = subprocess.run([
            "wasm-opt", "-Os", 
            "-o", str(optimized_wasm),
            str(optimized_wasm)
        ], capture_output=True, text=True)
        
        # Generate compilation report
        wasm_size = optimized_wasm.stat().st_size if optimized_wasm.exists() else 0
        
        return {
            "success": True,
            "wasm_file": str(optimized_wasm),
            "js_bindings": str(output_path / f"{crate_name}.js"),
            "size_bytes": wasm_size,
            "optimized": optimize_result.returncode == 0
        }
    
    def create_web_worker_loader(self, wasm_module: str, output_dir: str):
        """Create web worker loader for WASM module"""
        loader_template = f"""
// AI-NEXUS WASM Web Worker Loader
// Auto-generated for {wasm_module}

let wasmModule;

async function initWasm() {{
    try {{
        // Import WASM module
        const wasm = await import('./{wasm_module}.js');
        
        // Initialize WASM
        await wasm.default();
        wasmModule = wasm;
        
        // Notify main thread that WASM is ready
        self.postMessage({{ type: 'wasm_ready' }});
        
    }} catch (error) {{
        self.postMessage({{ 
            type: 'wasm_error', 
            error: error.message 
        }});
    }}
}}

// Handle messages from main thread
self.addEventListener('message', async function(event) {{
    const {{ type, data }} = event.data;
    
    switch (type) {{
        case 'init':
            await initWasm();
            break;
            
        case 'calculate_arbitrage':
            if (wasmModule) {{
                try {{
                    const result = wasmModule.calculate_arbitrage_profit(
                        data.priceA, 
                        data.priceB, 
                        data.amount, 
                        data.fees
                    );
                    self.postMessage({{
                        type: 'calculation_result',
                        result: result,
                        requestId: data.requestId
                    }});
                }} catch (error) {{
                    self.postMessage({{
                        type: 'calculation_error',
                        error: error.message,
                        requestId: data.requestId
                    }});
                }}
            }}
            break;
            
        case 'batch_calculate':
            if (wasmModule && wasmModule.batch_calculate_profits) {{
                try {{
                    const results = wasmModule.batch_calculate_profits(
                        new Float64Array(data.pricesA),
                        new Float64Array(data.pricesB),
                        new Float64Array(data.amounts),
                        new Float64Array(data.fees)
                    );
                    self.postMessage({{
                        type: 'batch_results',
                        results: Array.from(results),
                        requestId: data.requestId
                    }});
                }} catch (error) {{
                    self.postMessage({{
                        type: 'calculation_error',
                        error: error.message,
                        requestId: data.requestId
                    }});
                }}
            }}
            break;
    }}
}});

// Start initialization
initWasm();
"""
        
        loader_path = Path(output_dir) / f"{wasm_module}_worker.js"
        with open(loader_path, 'w') as f:
            f.write(loader_template)
        
        return str(loader_path)
    
    def generate_typescript_definitions(self, wasm_module: str, output_dir: str):
        """Generate TypeScript definitions for WASM module"""
        ts_definitions = f"""
// TypeScript definitions for {wasm_module} WASM module
// Auto-generated by AI-NEXUS WASM Compiler

declare module './{wasm_module}' {{
    /**
     * Initialize WASM module
     */
    export default function init(): Promise<void>;
    
    /**
     * Calculate arbitrage profit
     */
    export function calculate_arbitrage_profit(
        priceA: number,
        priceB: number, 
        amount: number,
        fees: number
    ): number;
    
    /**
     * Batch calculate multiple arbitrage opportunities
     */
    export function batch_calculate_profits(
        pricesA: Float64Array,
        pricesB: Float64Array,
        amounts: Float64Array,
        fees: Float64Array
    ): Float64Array;
    
    /**
     * Calculate triangular arbitrage opportunity
     */
    export function calculate_triangular_arbitrage(
        priceAB: number,
        priceBC: number,
        priceCA: number
    ): number;
    
    /**
     * Calculate slippage-adjusted price
     */
    export function calculate_slippage_price(
        reservesIn: number,
        reservesOut: number,
        amountIn: number,
        feeBps: number
    ): number;
    
    /**
     * Memory management functions
     */
    export interface WasmMemory {{
        buffer: ArrayBuffer;
    }}
    
    export const memory: WasmMemory;
}}

export default init;
"""
        
        ts_path = Path(output_dir) / f"{wasm_module}.d.ts"
        with open(ts_path, 'w') as f:
            f.write(ts_definitions)
        
        return str(ts_path)
    
    def create_benchmark_suite(self, wasm_module: str, output_dir: str):
        """Create performance benchmark suite for WASM module"""
        benchmark_js = f"""
// AI-NEXUS WASM Performance Benchmark
// Test suite for {wasm_module}

class WASMBenchmark {{
    constructor(wasmModule) {{
        this.wasm = wasmModule;
        this.results = {{}};
    }}
    
    async runBenchmarks() {{
        console.log('Running WASM performance benchmarks...');
        
        // Benchmark single calculation
        await this.benchmarkSingleCalculation();
        
        // Benchmark batch calculations
        await this.benchmarkBatchCalculations();
        
        // Benchmark memory usage
        await this.benchmarkMemoryUsage();
        
        return this.results;
    }}
    
    async benchmarkSingleCalculation() {{
        const iterations = 10000;
        const startTime = performance.now();
        
        for (let i = 0; i < iterations; i++) {{
            this.wasm.calculate_arbitrage_profit(
                100 + Math.random() * 10,
                105 + Math.random() * 10, 
                1.0,
                0.001
            );
        }}
        
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        this.results.singleCalculation = {{
            iterations: iterations,
            totalTime: duration,
            averageTime: duration / iterations,
            operationsPerSecond: (iterations / duration) * 1000
        }};
    }}
    
    async benchmarkBatchCalculations() {{
        const batchSize = 1000;
        const pricesA = new Float64Array(batchSize);
        const pricesB = new Float64Array(batchSize);
        const amounts = new Float64Array(batchSize);
        const fees = new Float64Array(batchSize);
        
        // Fill with test data
        for (let i = 0; i < batchSize; i++) {{
            pricesA[i] = 100 + Math.random() * 10;
            pricesB[i] = 105 + Math.random() * 10;
            amounts[i] = 1.0;
            fees[i] = 0.001;
        }}
        
        const startTime = performance.now();
        const results = this.wasm.batch_calculate_profits(pricesA, pricesB, amounts, fees);
        const endTime = performance.now();
        
        this.results.batchCalculation = {{
            batchSize: batchSize,
            totalTime: endTime - startTime,
            timePerCalculation: (endTime - startTime) / batchSize
        }};
    }}
    
    async benchmarkMemoryUsage() {{
        // Measure memory before operations
        const memoryBefore = this.wasm.memory.buffer.byteLength;
        
        // Perform memory-intensive operations
        const largeArray = new Float64Array(100000);
        for (let i = 0; i < largeArray.length; i++) {{
            largeArray[i] = Math.random();
        }}
        
        const memoryAfter = this.wasm.memory.buffer.byteLength;
        
        this.results.memoryUsage = {{
            initialMemory: memoryBefore,
            afterOperations: memoryAfter,
            memoryIncrease: memoryAfter - memoryBefore
        }};
    }}
}}

// Export for use in tests
window.WASMBenchmark = WASMBenchmark;
"""
        
        benchmark_path = Path(output_dir) / f"{wasm_module}_benchmark.js"
        with open(benchmark_path, 'w') as f:
            f.write(benchmark_js)
        
        return str(benchmark_path)
    
    def compile_full_pipeline(self, crate_name: str, output_dir: str) -> Dict:
        """Complete WASM compilation pipeline"""
        print(f"Starting full WASM compilation pipeline for {crate_name}...")
        
        try:
            # Setup toolchain
            self.setup_wasm_toolchain()
            
            # Compile to WASM
            compile_result = self.compile_to_wasm(crate_name, output_dir)
            if not compile_result['success']:
                return compile_result
            
            # Generate supporting files
            worker_loader = self.create_web_worker_loader(crate_name, output_dir)
            ts_definitions = self.generate_typescript_definitions(crate_name, output_dir)
            benchmark_suite = self.create_benchmark_suite(crate_name, output_dir)
            
            return {
                "success": True,
                "wasm_module": crate_name,
                "files": {
                    "wasm": compile_result['wasm_file'],
                    "js_bindings": compile_result['js_bindings'],
                    "web_worker": worker_loader,
                    "typescript_defs": ts_definitions,
                    "benchmark_suite": benchmark_suite
                },
                "metrics": {
                    "wasm_size_bytes": compile_result['size_bytes'],
                    "optimized": compile_result['optimized']
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Example usage
if __name__ == "__main__":
    compiler = WASMCompiler("./core/rust")
    
    # Compile arbitrage math module
    result = compiler.compile_full_pipeline(
        "arbitrage_math",
        "./dist/wasm"
    )
    
    if result['success']:
        print("WASM compilation successful!")
        print(f"WASM size: {result['metrics']['wasm_size_bytes']} bytes")
        print("Generated files:")
        for file_type, file_path in result['files'].items():
            print(f"  {file_type}: {file_path}")
    else:
        print(f"WASM compilation failed: {result['error']}")
