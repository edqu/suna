/**
 * Stagehand Browser Server for Windows Host
 * 
 * This server runs on your Windows machine (NOT in Docker) and provides
 * browser automation with a VISIBLE Chrome window that you can watch.
 * 
 * Setup:
 * 1. Install Node.js: https://nodejs.org/
 * 2. cd browser-server
 * 3. npm install
 * 4. Set GEMINI_API_KEY in .env
 * 5. node stagehand-server.js
 * 
 * The browser will open on your Windows desktop and you can watch it work!
 */

const express = require('express');
const { Stagehand } = require('@browserbasehq/stagehand');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 8004;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

// Browser automation state
let stagehand = null;
let page = null;
let browserInitialized = false;

/**
 * Initialize the Stagehand browser
 */
async function initBrowser(apiKey, modelName) {
    try {
        if (browserInitialized && stagehand && page) {
            console.log('Browser already initialized');
            return { status: 'healthy', message: 'Browser already running' };
        }

        // Clean up any existing browser
        if (stagehand && page) {
            console.log('Cleaning up existing browser...');
            await shutdown();
        }

        // Determine which vision model to use
        const visionModel = modelName || process.env.BROWSER_VISION_MODEL || 'google/gemini-2.5-pro';
        const isOllamaModel = visionModel.startsWith('ollama/');
        
        console.log(`Initializing Stagehand browser with vision model: ${visionModel}`);
        if (isOllamaModel) {
            console.log('✅ Using FREE local Ollama model (no API costs!)');
        } else {
            console.log('⚠️  Using cloud model (API costs apply)');
        }
        
        const modelConfig = {
            modelName: visionModel
        };
        
        // Configure model client options based on provider
        if (!isOllamaModel) {
            // Cloud models (Gemini, etc.) need API key
            modelConfig.modelClientOptions = {
                apiKey: apiKey || GEMINI_API_KEY
            };
        } else {
            // Ollama models need base URL
            const ollamaBase = process.env.OLLAMA_API_BASE || 'http://localhost:11434';
            modelConfig.modelClientOptions = {
                baseURL: ollamaBase
            };
            console.log(`Ollama server: ${ollamaBase}`);
        }
        
        stagehand = new Stagehand({
            env: 'LOCAL',
            enableCaching: true,
            verbose: 2,
            logger: (logLine) => {
                console.log(`[${logLine.category}] ${logLine.message}`);
            },
            ...modelConfig,
            localBrowserLaunchOptions: {
                headless: false,  // VISIBLE browser window!
                viewport: {
                    width: 1280,
                    height: 900
                },
                args: [
                    '--start-maximized',  // Start maximized for visibility
                    '--disable-blink-features=AutomationControlled',  // Less detectable
                ]
            }
        });

        await stagehand.init();
        page = stagehand.page;
        browserInitialized = true;

        // Handle browser/page close
        if (page) {
            page.on('close', () => {
                console.log('Browser page closed - resetting state');
                browserInitialized = false;
                page = null;
            });

            try {
                const browser = page.context().browser();
                browser?.on('disconnected', () => {
                    console.log('Browser disconnected - resetting state');
                    browserInitialized = false;
                    page = null;
                });
            } catch (err) {
                console.error('Failed to attach browser disconnect handler:', err);
            }
        }

        // Navigate to Google homepage initially
        await page.goto('https://www.google.com', { 
            waitUntil: 'domcontentloaded', 
            timeout: 30000 
        });

        console.log('✅ Browser initialized successfully - window should be visible!');
        
        return { 
            status: 'healthy', 
            message: 'Browser initialized and visible on Windows',
            url: page.url(),
            title: await page.title()
        };

    } catch (error) {
        console.error('Failed to initialize browser:', error);
        browserInitialized = false;
        throw error;
    }
}

/**
 * Shutdown the browser
 */
async function shutdown() {
    try {
        if (page) {
            await page.close();
        }
        if (stagehand) {
            // Stagehand cleanup if needed
            stagehand = null;
        }
        page = null;
        browserInitialized = false;
        console.log('Browser shut down');
    } catch (error) {
        console.error('Error during shutdown:', error);
    }
}

// =============================================================================
// API Endpoints
// =============================================================================

/**
 * Health check endpoint
 */
app.get('/api', (req, res) => {
    if (browserInitialized && page) {
        res.json({ 
            status: 'healthy',
            message: 'Browser is running',
            url: page.url()
        });
    } else {
        res.json({ 
            status: 'not_initialized',
            message: 'Browser not initialized. Call POST /api/init first.'
        });
    }
});

/**
 * Initialize browser
 */
app.post('/api/init', async (req, res) => {
    try {
        const { api_key, model_name } = req.body;
        const result = await initBrowser(api_key, model_name);
        res.json(result);
    } catch (error) {
        res.status(500).json({ 
            status: 'error', 
            error: error.message 
        });
    }
});

/**
 * Navigate to URL
 */
app.post('/api/navigate', async (req, res) => {
    try {
        if (!browserInitialized || !page) {
            return res.status(400).json({ 
                success: false, 
                error: 'Browser not initialized' 
            });
        }

        const { url } = req.body;
        
        console.log(`Navigating to: ${url}`);
        await page.goto(url, { 
            waitUntil: 'domcontentloaded', 
            timeout: 30000 
        });

        // Take screenshot
        const screenshot = await page.screenshot({ 
            type: 'png',
            fullPage: false 
        });

        res.json({
            success: true,
            message: `Navigated to ${url}`,
            url: page.url(),
            title: await page.title(),
            screenshot_base64: screenshot.toString('base64')
        });

    } catch (error) {
        console.error('Navigation error:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

/**
 * Perform browser action
 */
app.post('/api/act', async (req, res) => {
    try {
        if (!browserInitialized || !page || !stagehand) {
            return res.status(400).json({ 
                success: false, 
                error: 'Browser not initialized' 
            });
        }

        const { action, variables, iframes } = req.body;
        
        console.log(`Performing action: ${action}`);
        
        // Use Stagehand's act method
        const result = await stagehand.act({
            action,
            variables: variables || {},
            useVision: true,
            verifyActed: true
        });

        // Take screenshot after action
        const screenshot = await page.screenshot({ 
            type: 'png',
            fullPage: false 
        });

        res.json({
            success: true,
            message: `Performed action: ${action}`,
            action: action,
            url: page.url(),
            title: await page.title(),
            screenshot_base64: screenshot.toString('base64')
        });

    } catch (error) {
        console.error('Action error:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message,
            action: req.body.action
        });
    }
});

/**
 * Extract content from page
 */
app.post('/api/extract', async (req, res) => {
    try {
        if (!browserInitialized || !page || !stagehand) {
            return res.status(400).json({ 
                success: false, 
                error: 'Browser not initialized' 
            });
        }

        const { instruction, schema } = req.body;
        
        console.log(`Extracting content: ${instruction}`);
        
        // Use Stagehand's extract method
        const extractedData = await stagehand.extract({
            instruction,
            schema: schema || undefined,
            useVision: true
        });

        // Take screenshot
        const screenshot = await page.screenshot({ 
            type: 'png',
            fullPage: false 
        });

        res.json({
            success: true,
            message: 'Content extracted successfully',
            data: extractedData,
            url: page.url(),
            title: await page.title(),
            screenshot_base64: screenshot.toString('base64')
        });

    } catch (error) {
        console.error('Extraction error:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

/**
 * Take screenshot
 */
app.post('/api/screenshot', async (req, res) => {
    try {
        if (!browserInitialized || !page) {
            return res.status(400).json({ 
                success: false, 
                error: 'Browser not initialized' 
            });
        }

        const screenshot = await page.screenshot({ 
            type: 'png',
            fullPage: req.body.fullPage || false 
        });

        res.json({
            success: true,
            message: 'Screenshot captured',
            url: page.url(),
            title: await page.title(),
            screenshot_base64: screenshot.toString('base64')
        });

    } catch (error) {
        console.error('Screenshot error:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

/**
 * Shutdown browser
 */
app.post('/api/shutdown', async (req, res) => {
    try {
        await shutdown();
        res.json({ 
            success: true, 
            message: 'Browser shut down successfully' 
        });
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

// =============================================================================
// Server Startup
// =============================================================================

app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🌐 Stagehand Browser Server Running on Windows              ║
║                                                                ║
║   Port: ${PORT}                                                  ║
║   Status: http://localhost:${PORT}/api                          ║
║                                                                ║
║   The browser will open VISIBLY on your Windows desktop!      ║
║                                                                ║
║   Ready to receive commands from Docker container...          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    `);

    if (!GEMINI_API_KEY) {
        console.warn(`
⚠️  WARNING: GEMINI_API_KEY not found in environment!
    Browser initialization will fail without an API key.
    
    Get a free key: https://aistudio.google.com/app/apikey
    Then create a .env file with: GEMINI_API_KEY=your-key-here
        `);
    } else {
        console.log('✅ GEMINI_API_KEY configured');
    }
});

// Handle graceful shutdown
process.on('SIGINT', async () => {
    console.log('\nShutting down gracefully...');
    await shutdown();
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log('\nShutting down gracefully...');
    await shutdown();
    process.exit(0);
});
