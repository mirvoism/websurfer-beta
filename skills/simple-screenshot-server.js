#!/usr/bin/env node

/**
 * Simple Screenshot Server for WebSurfer-β
 * Captures and resizes screenshots to be LLM-friendly (600px max)
 * No external dependencies required
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');

const execAsync = promisify(exec);

class SimpleScreenshotServer {
    constructor() {
        this.setupStdioHandling();
    }

    setupStdioHandling() {
        // Handle JSON-RPC requests from stdin
        process.stdin.setEncoding('utf8');
        
        let buffer = '';
        process.stdin.on('data', (chunk) => {
            buffer += chunk;
            
            // Process complete lines
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer
            
            for (const line of lines) {
                if (line.trim()) {
                    this.handleRequest(line.trim());
                }
            }
        });

        process.stdin.on('end', () => {
            process.exit(0);
        });

        // Error handling
        process.on('SIGINT', () => {
            process.exit(0);
        });

        process.on('SIGTERM', () => {
            process.exit(0);
        });
    }

    async handleRequest(requestLine) {
        try {
            const request = JSON.parse(requestLine);
            
            if (request.method === 'tools/call' && 
                request.params && 
                request.params.name === 'screen_capture_safe') {
                
                const result = await this.screenCaptureSafe();
                
                const response = {
                    jsonrpc: "2.0",
                    id: request.id,
                    result: result
                };
                
                process.stdout.write(JSON.stringify(response) + '\n');
                
            } else {
                // Unknown method
                const error = {
                    jsonrpc: "2.0",
                    id: request.id,
                    error: {
                        code: -32601,
                        message: `Method not found: ${request.method}`
                    }
                };
                
                process.stdout.write(JSON.stringify(error) + '\n');
            }
            
        } catch (error) {
            // Parse error or execution error
            const errorResponse = {
                jsonrpc: "2.0",
                id: null,
                error: {
                    code: -32603,
                    message: error.message
                }
            };
            
            process.stdout.write(JSON.stringify(errorResponse) + '\n');
        }
    }

    async screenCaptureSafe() {
        try {
            const timestamp = Date.now();
            const tempFile = `/tmp/screenshot_${timestamp}.png`;
            
            // Capture screenshot
            await execAsync(`screencapture -x -t png "${tempFile}"`);
            
            // Check if file exists
            try {
                await fs.access(tempFile);
            } catch {
                throw new Error('Screenshot capture failed');
            }
            
            // Resize to 600px max
            await execAsync(`sips -Z 600 "${tempFile}"`);
            
            // Read the resized image
            const imageData = await fs.readFile(tempFile);
            const base64Data = imageData.toString('base64');
            
            // Get file size for reporting
            const fileSizeKB = Math.round(base64Data.length / 1024);
            
            // Cleanup
            await fs.unlink(tempFile).catch(() => {});
            
            return {
                content: [{
                    type: 'text',
                    text: `Screenshot captured (scaled to 600px max, size: ${fileSizeKB}KB)`
                }, {
                    type: 'image',
                    data: base64Data,
                    mimeType: 'image/png'
                }]
            };
            
        } catch (error) {
            throw new Error(`Screenshot failed: ${error.message}`);
        }
    }
}

// Start the server
const server = new SimpleScreenshotServer();
console.error("Simple Screenshot Server running on stdio"); 