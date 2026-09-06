# 🚀 TestPilot AI

### AI-Powered Software Testing, Automation & Bug Intelligence Platform

TestPilot AI is an AI-powered software testing platform that helps developers and testers generate test cases, run automated tests, analyze failures, and understand bugs faster.

The platform combines AI, automated testing, and a simple dashboard to make software testing easier and more efficient.

---

## 🎯 Objectives

- Generate test cases automatically from software requirements.
- Convert requirements into executable test code.
- Run automated API and browser tests.
- Analyze test failures using AI.
- Identify the possible reason for a failed test.
- Classify bugs into different categories.
- Detect flaky tests using test run history.
- Prioritize bugs based on their severity.
- Provide a testing dashboard for better monitoring.

---

## ✨ Key Features

### 🧪 AI Test Case Generator
Generate test cases from natural-language software requirements using AI.

### ⚙️ Automated Test Execution
Execute generated tests using tools such as Pytest and Playwright.

### 🔍 AI Failure Analysis
Analyze errors, stack traces, logs, and test results to identify possible causes.

### 🐞 Bug Intelligence
Classify failures into categories such as:

- BUG
- ENVIRONMENT ISSUE
- TEST SCRIPT ISSUE
- NETWORK ISSUE
- DEPENDENCY ISSUE
- FLAKY TEST
- PERFORMANCE ISSUE
- SECURITY ISSUE

### 🔄 Flaky Test Detection
Use previous test results to identify tests that sometimes pass and sometimes fail.

### 📊 Test Dashboard
View test results, failures, bugs, and project information from one dashboard.

### 🔐 Authentication
Secure user registration and login using JWT authentication.

### 🗄️ Database
Store users, projects, requirements, test cases, test runs, and failure analysis data using PostgreSQL.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │     React Frontend  │
                    │   TypeScript + UI   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Flask Backend    │
                    │      REST APIs      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐     ┌───────────┐    ┌───────────┐
        │ AI Layer │     │ PostgreSQL│    │ Test      │
        │   LLM    │     │ Database  │    │ Execution │
        └──────────┘     └───────────┘    └───────────┘