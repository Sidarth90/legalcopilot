/*
Contract Explainer - Load Testing Script
Performance testing using k6
*/

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

// Test configuration
export const options = {
  scenarios: {
    // Gradual ramp-up test
    ramp_up: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 10 },   // Ramp up to 10 VUs over 2 minutes
        { duration: '5m', target: 10 },   // Stay at 10 VUs for 5 minutes
        { duration: '2m', target: 20 },   // Ramp up to 20 VUs over 2 minutes
        { duration: '5m', target: 20 },   // Stay at 20 VUs for 5 minutes
        { duration: '2m', target: 0 },    // Ramp down to 0 VUs over 2 minutes
      ],
      gracefulRampDown: '30s',
    },
    
    // Spike test
    spike_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 5 },    // Normal load
        { duration: '30s', target: 50 },  // Spike to 50 VUs
        { duration: '1m', target: 5 },    // Return to normal
      ],
      startTime: '18m', // Start after ramp_up test
    }
  },
  
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
    http_reqs: ['rate>10'],            // Must handle at least 10 requests per second
  },
};

// Environment configuration
const BASE_URL = __ENV.TARGET_URL || 'http://localhost:5001';

// Sample contract text for testing
const sampleContracts = new SharedArray('contracts', function () {
  return [
    'This is a sample employment contract between Company XYZ and John Doe. The employee agrees to work full-time for a salary of $50,000 per year. The contract includes standard terms and conditions.',
    'Non-disclosure agreement between parties. The receiving party agrees to keep confidential information secret. This agreement is valid for 5 years from the signing date.',
    'Service agreement for web development services. The contractor will provide website development services for $10,000. Project completion is expected within 3 months.',
  ];
});

export function setup() {
  // Verify the application is running
  const healthCheck = http.get(`${BASE_URL}/health`);
  check(healthCheck, {
    'Health check passes': (r) => r.status === 200,
  });
  
  console.log(`Starting load test against: ${BASE_URL}`);
}

export default function () {
  // Test homepage
  const homepageResponse = http.get(BASE_URL);
  check(homepageResponse, {
    'Homepage loads': (r) => r.status === 200,
    'Homepage contains title': (r) => r.body.includes('Contract Explainer'),
    'Homepage loads quickly': (r) => r.timings.duration < 1000,
  });
  
  sleep(1);
  
  // Test health endpoint
  const healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'Health endpoint responds': (r) => r.status === 200,
    'Health endpoint is fast': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
  
  // Test file upload endpoint (with text file)
  const contractText = sampleContracts[Math.floor(Math.random() * sampleContracts.length)];
  
  const formData = {
    file: http.file(Buffer.from(contractText), 'contract.txt', 'text/plain'),
  };
  
  const uploadResponse = http.post(`${BASE_URL}/api/analyze`, formData);
  check(uploadResponse, {
    'File upload accepted or rejected gracefully': (r) => [200, 400, 429].includes(r.status),
    'Upload response time acceptable': (r) => r.timings.duration < 30000, // 30s timeout
  });
  
  if (uploadResponse.status === 200) {
    check(uploadResponse, {
      'Analysis contains expected structure': (r) => {
        try {
          const json = JSON.parse(r.body);
          return json.success === true && json.analysis && json.filename;
        } catch (e) {
          return false;
        }
      },
    });
  }
  
  // Random sleep to simulate real user behavior
  sleep(Math.random() * 3 + 1); // 1-4 seconds
}

export function teardown(data) {
  console.log('Load test completed');
}

/*
Usage:
k6 run load-test.js

With custom target:
TARGET_URL=https://your-domain.com k6 run load-test.js

With different test duration:
k6 run --duration 30s --vus 10 load-test.js
*/