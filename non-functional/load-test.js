// ==========================================
// K6 NON-FUNCTIONAL TESTING SUITE
// ==========================================

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Counter, Rate, Trend } from "k6/metrics";

// Custom Metrics
const loginErrors = new Counter("login_errors");
const loginSuccessRate = new Rate("login_success_rate");
const apiResponseTime = new Trend("api_response_time");

// Test Configuration
export const options = {
  // Pilih salah satu scenario di bawah dengan uncomment

  // SCENARIO 1: Load Testing - Normal Load
  stages: [
    { duration: "2m", target: 10 }, // Ramp up to 10 users
    { duration: "5m", target: 10 }, // Stay at 10 users
    { duration: "2m", target: 20 }, // Ramp up to 20 users
    { duration: "5m", target: 20 }, // Stay at 20 users
    { duration: "2m", target: 0 }, // Ramp down to 0
  ],

  // SCENARIO 2: Stress Testing - Breaking Point (uncomment to use)
  // stages: [
  //   { duration: '2m', target: 50 },   // Ramp up to 50
  //   { duration: '5m', target: 50 },   // Stay at 50
  //   { duration: '2m', target: 100 },  // Push to 100
  //   { duration: '5m', target: 100 },  // Stay at 100
  //   { duration: '2m', target: 150 },  // Push to 150
  //   { duration: '5m', target: 150 },  // Stay at 150
  //   { duration: '3m', target: 0 },    // Ramp down
  // ],

  // SCENARIO 3: Spike Testing (uncomment to use)
  // stages: [
  //   { duration: '1m', target: 10 },   // Normal load
  //   { duration: '30s', target: 100 }, // Sudden spike
  //   { duration: '1m', target: 100 },  // Stay at spike
  //   { duration: '30s', target: 10 },  // Back to normal
  //   { duration: '1m', target: 10 },   // Stay at normal
  //   { duration: '30s', target: 0 },   // Ramp down
  // ],

  thresholds: {
    http_req_duration: ["p(95)<500"], // 95% requests < 500ms
    http_req_failed: ["rate<0.05"], // Error rate < 5%
    login_success_rate: ["rate>0.95"], // Login success > 95%
  },
};

// Configuration
const BASE_URL = "http://localhost:5000"; // Sesuaikan dengan URL API Anda
const CREDENTIALS = {
  owner: { email: "jose@aventra.com", password: "jose1234" },
  manager: { email: "verstappen@aventra.com", password: "maxmaxmax" },
  employee: { email: "piastri@aventra.com", password: "piastri123" },
};

// Helper: Login and get token
function login(email, password) {
  const res = http.post(
    `${BASE_URL}/auth/login`,
    JSON.stringify({
      email: email,
      password: password,
    }),
    {
      headers: { "Content-Type": "application/json" },
    }
  );

  const success = check(res, {
    "login status is 200": (r) => r.status === 200,
    "login returns token": (r) => r.cookies.token !== undefined,
  });

  if (success) {
    loginSuccessRate.add(1);
    return res.cookies.token[0].value;
  } else {
    loginErrors.add(1);
    loginSuccessRate.add(0);
    return null;
  }
}

// Main Test Scenario
export default function () {
  let token = null;

  // ==========================================
  // 1. AUTHENTICATION TESTING
  // ==========================================
  group("Authentication", () => {
    // Login as different roles
    const role = ["owner", "manager", "employee"][
      Math.floor(Math.random() * 3)
    ];
    const creds = CREDENTIALS[role];

    token = login(creds.email, creds.password);

    if (token) {
      // Get current user
      const currentUserRes = http.get(`${BASE_URL}/auth/current`, {
        cookies: { token: token },
      });

      check(currentUserRes, {
        "current user status is 200": (r) => r.status === 200,
        "current user has data": (r) => JSON.parse(r.body)._id !== undefined,
      });

      apiResponseTime.add(currentUserRes.timings.duration);
    }

    sleep(1);
  });

  if (!token) return; // Skip if login failed

  // ==========================================
  // 2. EMPLOYEE MANAGEMENT TESTING
  // ==========================================
  group("Employee Management", () => {
    // Get all employees
    const allEmpRes = http.get(`${BASE_URL}/api/employees/all`, {
      cookies: { token: token },
    });

    check(allEmpRes, {
      "get employees status is 200": (r) => r.status === 200,
      "employees response has data": (r) => {
        const body = JSON.parse(r.body);
        return body.status === true && Array.isArray(body.data);
      },
    });

    apiResponseTime.add(allEmpRes.timings.duration);

    // Get employee profile
    const profileRes = http.get(`${BASE_URL}/api/employees/profile`, {
      cookies: { token: token },
    });

    check(profileRes, {
      "profile status is 200": (r) => r.status === 200,
      "profile has employee data": (r) => {
        const body = JSON.parse(r.body);
        return body.data && body.data._id;
      },
    });

    sleep(1);
  });

  // ==========================================
  // 3. BRANCH/STORE MANAGEMENT TESTING
  // ==========================================
  group("Branch Management", () => {
    // Get active branches
    const activeBranchRes = http.get(`${BASE_URL}/api/branch/active`, {
      cookies: { token: token },
    });

    console.log("activeBranchRes", activeBranchRes);

    check(activeBranchRes, {
      "active branches status is 200": (r) => r.status === 200,
      "active branches has data": (r) => {
        const body = JSON.parse(r.body);
        return body.status === true && Array.isArray(body.data);
      },
    });

    apiResponseTime.add(activeBranchRes.timings.duration);

    // Get all branches
    const allBranchRes = http.get(`${BASE_URL}/api/branch`, {
      cookies: { token: token },
    });

    check(allBranchRes, {
      "all branches status is 200": (r) => r.status === 200,
    });

    sleep(1);
  });

  // ==========================================
  // 4. LEAVE REQUEST TESTING
  // ==========================================
  group("Leave Request", () => {
    // Get employee leave requests
    const empLeaveRes = http.get(
      `${BASE_URL}/api/annualRequest/list-employee`,
      {
        cookies: { token: token },
      }
    );

    check(empLeaveRes, {
      "employee leave list status is 200": (r) => r.status === 200,
    });

    // Get manager leave requests (may fail for employee role)
    const mgrLeaveRes = http.get(`${BASE_URL}/api/annualRequest/list-manager`, {
      cookies: { token: token },
    });

    check(mgrLeaveRes, {
      "manager leave list accessible": (r) =>
        r.status === 200 || r.status === 403,
    });

    apiResponseTime.add(empLeaveRes.timings.duration);

    sleep(1);
  });

  // ==========================================
  // 5. HISTORY TESTING
  // ==========================================
  group("History", () => {
    // Get user history
    const historyRes = http.get(`${BASE_URL}/api/history/all/user`, {
      cookies: { token: token },
    });

    check(historyRes, {
      "user history status is 200": (r) => r.status === 200,
      "history has data structure": (r) => {
        const body = JSON.parse(r.body);
        return body.status !== undefined;
      },
    });

    apiResponseTime.add(historyRes.timings.duration);

    sleep(1);
  });

  // ==========================================
  // 6. CONCURRENT OPERATIONS TESTING
  // ==========================================
  group("Concurrent Operations", () => {
    const requests = [
      ["GET", `${BASE_URL}/api/employees/profile`],
      ["GET", `${BASE_URL}/api/branch/active`],
      ["GET", `${BASE_URL}/api/history/all/user`],
      ["GET", `${BASE_URL}/api/annualRequest/list-employee`],
    ];

    const responses = http.batch(
      requests.map(([method, url]) => ({
        method: method,
        url: url,
        params: { cookies: { token: token } },
      }))
    );

    responses.forEach((res, idx) => {
      check(res, {
        [`concurrent request ${idx + 1} succeeded`]: (r) => r.status === 200,
      });
    });

    sleep(1);
  });

  // ==========================================
  // 7. LOGOUT
  // ==========================================
  group("Logout", () => {
    const logoutRes = http.post(`${BASE_URL}/auth/logout`, null, {
      cookies: { token: token },
    });

    check(logoutRes, {
      "logout status is 200": (r) => r.status === 200,
      "logout successful": (r) => {
        const body = JSON.parse(r.body);
        return body.status === true;
      },
    });

    sleep(1);
  });
}

// Teardown function
export function teardown(data) {
  console.log("========================================");
  console.log("Test Summary:");
  console.log("========================================");
  console.log("Test completed successfully");
  console.log("Check the K6 output for detailed metrics");
}
