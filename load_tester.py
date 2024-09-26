import asyncio
import httpx
import time

async def send_request(url):
    async with httpx.AsyncClient(timeout=30) as client:
        #response = await client.get(url)
        try:
            response = await client.get(url)
            # Detailed status code checking
            if response.status_code == 200:
                print(f"Response status: {response.status_code} | Content: {response.text[:100]}")
            else:
                print(f"Error: Received status code {response.status_code} | Content: {response.text[:100]}")
        except Exception as e:
            print(f"Request failed: {e}")

async def load_test(url, total_requests, concurrency, maxDoc):
    tasks = []
    for i in range(total_requests):
        tasks.append(send_request(url.format(urlId=i % maxDoc)))
        if len(tasks) >= concurrency:
            await asyncio.gather(*tasks)
            tasks = []
    # Gather any remaining tasks
    if tasks:
        await asyncio.gather(*tasks)

def main():
    url = "http://127.0.0.1:8000/stream?urlId={urlId}"  # Change to your FastAPI endpoint
    total_requests = 1000  # Total number of requests to send
    concurrency = 100      # Number of concurrent requests
    maxDoc = 5

    start_time = time.time()
    asyncio.run(load_test(url, total_requests, concurrency, maxDoc))
    end_time = time.time()

    print(f"Load test completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()