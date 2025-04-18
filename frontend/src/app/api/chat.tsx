interface ApiResponse {
  response: string | { message?: string; final_answer?: string; [key: string]: any };
  source?: string;
}

export const sendMessage = async (message: string, retries = 3): Promise<ApiResponse> => {
    try {
      console.log('Sending request to backend...');
      const startTime = Date.now();
      
      // Create abort controller with longer timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        if (!controller.signal.aborted) {
          controller.abort('Request timeout');
        }
      }, 30000); // 30s timeout
      
      let res;
      try {
        res = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message }),
          signal: controller.signal
        });
      } finally {
        clearTimeout(timeoutId);
      }
      console.log(`Request completed in ${Date.now() - startTime}ms`);
      console.log('Received response:', {
        status: res.status,
        statusText: res.statusText,
        headers: Object.fromEntries(res.headers.entries()),
        body: await res.clone().text()
      });

      if (!res.ok) {
        console.error('Full error response:', {
          status: res.status,
          headers: Object.fromEntries(res.headers.entries()),
          body: await res.clone().text()
        });
        let errorData: { error?: string; message?: string } = {};
        try {
          const text = await res.text();
          try {
            errorData = JSON.parse(text);
          } catch {
            errorData.error = text || res.statusText || `HTTP ${res.status}`;
          }
        } catch (e) {
          errorData.error = `Request failed with status ${res.status}`;
        }
        
        if (!errorData.error && !errorData.message) {
          errorData.error = 'Unknown error occurred';
        }
        
        console.error('Backend Error:', {
          status: res.status,
          statusText: res.statusText,
          error: errorData.error || errorData.message
        });
        
        // Handle timeout specifically
        if (res.status === 504) {
          if (retries > 0) {
            console.log(`Retrying... attempts left: ${retries}`);
            await new Promise(resolve => setTimeout(resolve, 1000 * (4 - retries))); // Exponential backoff
            return sendMessage(message, retries - 1);
          }
          throw new Error('The request took too long. Please try again with a more specific query.');
        }
        
        throw new Error(errorData.error || `HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      if (!data?.response) {
        throw new Error('Empty response from server');
      }
      
      // Handle both simple strings and complex responses
      if (typeof data.response === 'object') {
        return data.response.message || 
               data.response.final_answer || 
               JSON.stringify(data.response);
      }
      return {
        response: data.response,
        source: data.source || 'assistant'
      };
    } catch (error) {
      console.error('API Call Failed:', error);
      
      if (error instanceof Error && error.name === 'AbortError') {
        if (retries > 0) {
          console.log(`Retrying... attempts left: ${retries}`);
          await new Promise(resolve => setTimeout(resolve, 2000 * (4 - retries))); // Longer backoff
          return sendMessage(message, retries - 1);
        }
        return {
          response: '⚠️ The request timed out. The server might be busy. Please try again later.',
          source: 'error'
        };
      }
      
      if (error instanceof Error) {
        try {
          const errorData = JSON.parse(error.message);
          if (errorData.error === 'timeout') {
          return {
            response: `⚠️ ${errorData.message}`,
            source: 'error'
          };
          }
          return {
            response: `⚠️ ${errorData.message || 'Service unavailable. Please try again.'}`,
            source: 'error'
          };
        } catch {
          return {
            response: `⚠️ ${error.message}`,
            source: 'error'
          };
        }
      }
      return {
        response: '⚠️ Network error - please check your connection',
        source: 'error'
      };
    }
  };
  