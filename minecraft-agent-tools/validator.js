const http = require('http');

const TARGET_URL = process.argv[2] && !process.argv[2].startsWith('--') 
  ? process.argv[2] 
  : 'http://localhost:3001';

console.log(`Starting Arenex Bot Validation Suite against ${TARGET_URL}...`);

function makeRequest(method, path) {
  return new Promise((resolve, reject) => {
    const req = http.request(`${TARGET_URL}${path}`, { method, timeout: 5000 }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ statusCode: res.statusCode, data: JSON.parse(data) });
        } catch (e) {
          reject(new Error(`Failed to parse JSON response from ${path}: ${data}`));
        }
      });
    });
    req.on('timeout', () => {
      req.destroy();
      reject(new Error(`Request to ${path} timed out after 5000ms`));
    });
    req.on('error', (err) => reject(new Error(`Connection failed: ${err.message}`)));
    req.end();
  });
}

function assertShape(obj, schemaPath, expectedType) {
  const value = schemaPath.split('.').reduce((acc, part) => acc && acc[part], obj);
  if (typeof value !== expectedType) {
    throw new Error(`Validation failed for '${schemaPath}'. Expected type '${expectedType}', got '${typeof value}'`);
  }
}

async function runValidation() {
  try {
    console.log('\n[1/3] Testing GET /health...');
    const health = await makeRequest('GET', '/health');
    console.log('Response:', health.data);
    if (health.statusCode !== 200) throw new Error(`Expected 200 OK, got ${health.statusCode}`);
    assertShape(health.data, 'status', 'string');
    assertShape(health.data, 'bot_connected', 'boolean');
    console.log('✓ /health passed');

    console.log('\n[2/3] Testing GET /status...');
    const status = await makeRequest('GET', '/status');
    console.log('Response:', status.data);
    if (status.statusCode !== 200) throw new Error(`Expected 200 OK, got ${status.statusCode}`);
    
    // Strict schema check mirroring the Arenex Python Match Runner expectations
    const data = status.data;
    assertShape(data, 'bot', 'string');
    assertShape(data, 'match_id', 'string');
    assertShape(data, 'position.x', 'number');
    assertShape(data, 'position.y', 'number');
    assertShape(data, 'position.z', 'number');
    assertShape(data, 'wood_count', 'number');
    assertShape(data, 'current_action', 'string');
    assertShape(data, 'health', 'number');
    assertShape(data, 'food', 'number');
    assertShape(data, 'inventory_fullness', 'number');
    
    console.log('✓ /status JSON Schema perfectly matches Arenex standard');

    console.log('\n[3/3] Testing POST /stop...');
    // We only test /stop if explicitly requested because it enforces node termination
    if (process.argv.includes('--test-stop')) {
      const stop = await makeRequest('POST', '/stop');
      console.log('Response:', stop.data);
      if (stop.statusCode !== 200) throw new Error(`Expected 200 OK, got ${stop.statusCode}`);
      assertShape(stop.data, 'status', 'string');
      console.log('✓ /stop sequence initiated. Bot process should securely exit within seconds.');
    } else {
      console.log('Skipping /stop test. Use --test-stop flag to explicitly trigger termination.');
    }

    console.log('\n✅ VALIDATION PASSED! Your bot is correctly shaped for Arenex match runner injection.');

  } catch (err) {
    console.error('\n❌ VALIDATION FAILED:', err.message);
    process.exit(1);
  }
}

runValidation();
