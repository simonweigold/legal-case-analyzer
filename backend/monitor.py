#!/usr/bin/env python3
"""
Simple monitoring script to check backend performance and identify issues.
Run this while your backend is running to get insights.
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_endpoint(session, endpoint, method="GET", data=None):
    """Test a single endpoint and measure response time."""
    start_time = time.time()
    try:
        if method == "GET":
            async with session.get(f"{BASE_URL}{endpoint}") as response:
                status = response.status
                response_time = time.time() - start_time
                return {
                    "endpoint": endpoint,
                    "method": method,
                    "status": status,
                    "response_time": response_time,
                    "success": 200 <= status < 300
                }
        elif method == "POST":
            async with session.post(f"{BASE_URL}{endpoint}", json=data) as response:
                status = response.status
                response_time = time.time() - start_time
                return {
                    "endpoint": endpoint,
                    "method": method,
                    "status": status,
                    "response_time": response_time,
                    "success": 200 <= status < 300
                }
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "endpoint": endpoint,
            "method": method,
            "status": 0,
            "response_time": response_time,
            "success": False,
            "error": str(e)
        }

async def monitor_backend():
    """Monitor backend performance."""
    print(f"🔍 Monitoring backend at {BASE_URL}")
    print(f"⏰ Started at {datetime.now()}")
    print("-" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test basic endpoints
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/docs", "GET"),
        ]
        
        results = []
        for endpoint, method in endpoints:
            result = await test_endpoint(session, endpoint, method)
            results.append(result)
            
            status_emoji = "✅" if result["success"] else "❌"
            print(f"{status_emoji} {method:4} {endpoint:20} | "
                  f"Status: {result['status']:3} | "
                  f"Time: {result['response_time']:.3f}s")
            
            if not result["success"] and "error" in result:
                print(f"   Error: {result['error']}")
        
        print("-" * 60)
        
        # Calculate averages
        successful_requests = [r for r in results if r["success"]]
        if successful_requests:
            avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            print(f"📊 Average response time: {avg_response_time:.3f}s")
        
        success_rate = len(successful_requests) / len(results) * 100
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        if success_rate < 100:
            failed_requests = [r for r in results if not r["success"]]
            print(f"⚠️  Failed endpoints: {[r['endpoint'] for r in failed_requests]}")

if __name__ == "__main__":
    asyncio.run(monitor_backend())
