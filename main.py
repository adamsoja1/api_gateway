from fastapi import FastAPI, Request, HTTPException
import httpx

app = FastAPI()

SERVICE_URLS = {
    "auth_service": "http://auth_service:8000",
    "patients_service": "http://patients_service:8000"
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):

    if service not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail="Service not found")
    
    url = f"{SERVICE_URLS[service]}/{path}"
    method = request.method
    headers = dict(request.headers)
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method in ["POST", "PUT"]:
                try:
                    body = await request.body()
                except Exception as e:
                    print(f"Error reading body from request: {e}")
                    raise HTTPException(status_code=400, detail="Invalid body data")
           
                response = await client.request(method, url, headers=headers, content=body)
                
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
        
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}. Exception: {exc}")
            raise HTTPException(status_code=500, detail="Internal server error") from exc
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}. Response: {exc.response.text}")
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc

    return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
