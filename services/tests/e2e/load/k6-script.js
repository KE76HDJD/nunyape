import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const paymentSuccessRate = new Rate('payment_success_rate');
const presentationCreationTrend = new Trend('presentation_creation_time');
const failedRequests = new Counter('failed_requests');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 50 },  // Ramp up to 50 users
    { duration: '5m', target: 50 },  // Stay at 50 users
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 50 },  // Ramp down to 50 users
    { duration: '2m', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],   // Less than 1% failures
    payment_success_rate: ['rate>0.95'], // 95% payment success
  },
};

// Base URLs
const BASE_URLS = {
  auth: __ENV.AUTH_URL || 'http://localhost:8000',
  payment: __ENV.PAYMENT_URL || 'http://localhost:8080',
  presentation: __ENV.PRESENTATION_URL || 'http://localhost:8001',
  qa: __ENV.QA_URL || 'http://localhost:8081',
};

// Global variables
let authToken = '';
let userId = '';

export function setup() {
  // Setup: Get authentication token
  const loginPayload = JSON.stringify({
    email: 'load_test@company.com',
    password: 'LoadTestPass123!'
  });

  const loginParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const loginRes = http.post(`${BASE_URLS.auth}/api/v1/token`, loginPayload, loginParams);
  
  if (loginRes.status !== 200) {
    throw new Error(`Failed to get auth token: ${loginRes.status}`);
  }

  const loginData = JSON.parse(loginRes.body);
  return {
    authToken: loginData.access_token,
    userId: loginData.user_id || 'load_test_user'
  };
}

export default function(data) {
  authToken = data.authToken;
  userId = data.userId;

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`,
  };

  // Test sequence: Payment -> Presentation -> QA
  const testStartTime = new Date().getTime();

  // 1. Create a payment
  const paymentPayload = JSON.stringify({
    amount: Math.random() * 100 + 1, // Random amount between 1-101
    currency: 'USD',
    payment_method: 'credit_card',
    customer_id: `load_test_customer_${__VU}_${__ITER}`,
    order_id: `order_${Date.now()}_${__VU}_${__ITER}`,
    description: 'Load test payment'
  });

  const paymentRes = http.post(`${BASE_URLS.payment}/api/v1/payments`, paymentPayload, { headers });
  
  const paymentSuccess = check(paymentRes, {
    'payment creation status is 200': (r) => r.status === 200,
    'payment has ID': (r) => JSON.parse(r.body).id !== undefined,
  });

  paymentSuccessRate.add(paymentSuccess);

  if (!paymentSuccess) {
    failedRequests.add(1);
    console.log(`Payment failed: ${paymentRes.status} - ${paymentRes.body}`);
  }

  const paymentId = paymentSuccess ? JSON.parse(paymentRes.body).id : null;

  // 2. Create a presentation
  if (paymentSuccess) {
    const presentationPayload = JSON.stringify({
      presentation: {
        title: `Load Test Presentation ${__VU}-${__ITER}`,
        description: 'Presentation created during load testing',
        theme: 'modern',
        tags: ['load-test', `vu-${__VU}`]
      },
      slides: [
        {
          title: 'Welcome Slide',
          content: 'This presentation was created during load testing',
          slide_type: 'title',
          order: 1
        },
        {
          title: 'Content Slide',
          content: 'This is the content of the load test presentation',
          slide_type: 'content',
          order: 2
        }
      ]
    });

    const presentationRes = http.post(
      `${BASE_URLS.presentation}/api/v1/presentations`, 
      presentationPayload, 
      { headers }
    );

    const presentationSuccess = check(presentationRes, {
      'presentation creation status is 200': (r) => r.status === 200,
      'presentation has ID': (r) => JSON.parse(r.body).id !== undefined,
    });

    if (presentationSuccess) {
      const creationTime = new Date().getTime() - testStartTime;
      presentationCreationTrend.add(creationTime);
    } else {
      failedRequests.add(1);
    }
  }

  // 3. Use QA service
  const questions = [
    'What is microservices architecture?',
    'How to handle authentication in APIs?',
    'What are the benefits of cloud computing?',
    'How does load balancing work?',
    'What is containerization?'
  ];

  const randomQuestion = questions[Math.floor(Math.random() * questions.length)];
  const qaPayload = JSON.stringify({
    question: randomQuestion,
    max_results: 3
  });

  const qaRes = http.post(`${BASE_URLS.qa}/api/v1/qa/ask`, qaPayload, { headers });

  check(qaRes, {
    'QA service status is 200': (r) => r.status === 200,
    'QA service returns answer': (r) => JSON.parse(r.body).answer.length > 0,
  });

  // 4. Simulate some browsing behavior
  const browseEndpoints = [
    `${BASE_URLS.presentation}/api/v1/presentations`,
    `${BASE_URLS.qa}/api/v1/qa/stats`,
    `${BASE_URLS.auth}/api/v1/users/me`
  ];

  browseEndpoints.forEach(endpoint => {
    const browseRes = http.get(endpoint, { headers });
    check(browseRes, {
      [`browse ${endpoint} status is 200`]: (r) => r.status === 200,
    });
  });

  // Think time between iterations
  sleep(Math.random() * 2 + 1); // 1-3 seconds
}

export function teardown(data) {
  console.log('Load test completed');
  console.log(`Auth token used: ${data.authToken ? 'Yes' : 'No'}`);
}