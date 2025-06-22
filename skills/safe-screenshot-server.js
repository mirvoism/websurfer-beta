#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema, McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";
import { exec } from 'child_process';
import { promisify } from 'util';
import { readFile, unlink } from 'fs/promises';

const execAsync = promisify(exec);

class SafeScreenshotServer {
    constructor() {
        this.server = new Server({
            name: "safe-screenshot-server",
            version: "1.0.0",
        }, {
            capabilities: {
                tools: {},
            },
        });

        this.setupToolHandlers();

        // Error handling
        this.server.onerror = (error) => console.error("[MCP Error]", error);
        process.on("SIGINT", async () => {
            await this.server.close();
            process.exit(0);
        });
    }

    setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [{
                name: 'screen_capture_safe',
                description: 'Takes a screenshot scaled to fit MCP size limits (max 600px)',
                inputSchema: { 
                    type: 'object', 
                    properties: {},
                    required: []
                }
            }]
        }));

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name } = request.params;

            if (name === 'screen_capture_safe') {
                return await this.screenCaptureSafe();
            }
            
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
        });
    }

    async screenCaptureSafe() {
        try {
            const timestamp = Date.now();
            const tempFile = `/tmp/screenshot_${timestamp}.png`;
            
            // Capture and scale in one command
            await execAsync(`screencapture -x -t png "${tempFile}" && sips -Z 600 "${tempFile}"`);
            
            const imageData = await readFile(tempFile);
            const base64Data = imageData.toString('base64');
            
            // Cleanup
            await unlink(tempFile).catch(() => {});
            
            return {
                content: [{
                    type: 'text',
                    text: `Screenshot captured (scaled to 600px max, size: ${Math.round(base64Data.length/1024)}KB)`
                }, {
                    type: 'image',
                    data: base64Data,
                    mimeType: 'image/png'
                }]
            };
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            throw new McpError(ErrorCode.InternalError, errorMessage);
        }
    }

    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error("Safe Screenshot MCP server running on stdio");
    }
}

const server = new SafeScreenshotServer();
server.run().catch(console.error);
