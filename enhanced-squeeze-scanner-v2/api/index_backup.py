from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import urllib.request
import os
from datetime import datetime
import time

class handler(BaseHTTPRequestHandler):
    
    def validate_ortex_api_key(self, ortex_key):
        """Advanced Ortex API debugging - Let's figure out what they want!"""
        if not ortex_key or len(ortex_key) < 10:
            return {'valid': False, 'message': 'API key too short or empty'}
        
        print(f"🔧 DEEP DEBUGGING Ortex API key: {ortex_key[:15]}...")
        
        # Let's try multiple API domains and formats
        api_domains = [
            'https://api.ortex.com',
            'https://rest.ortex.com', 
            'https://data.ortex.com',
            'https://api-v2.ortex.com',
            'https://gateway.ortex.com'
        ]
        
        # Test simple endpoints first
        simple_tests = [
            '/health',
            '/status', 
            '/api/status',
            '/api/v1/status',
            '/api/v2/status',
            '/ping'
        ]
        
        validation_results = []
        
        # First, test if any domain responds to simple health checks
        print("🔍 Phase 1: Testing API domain accessibility...")
        for domain in api_domains:
            for test_path in simple_tests:
                test_url = f"{domain}{test_path}"
                
                try:
                    req = urllib.request.Request(test_url)
                    req.add_header('User-Agent', 'Ultimate-Squeeze-Scanner/1.0')
                    req.add_header('Accept', 'application/json')
                    req.add_header('Ortex-Api-Key', ortex_key)
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        status = response.getcode()
                        content_type = response.headers.get('Content-Type', 'unknown')
                        data = response.read()[:500].decode('utf-8', errors='ignore')
                        
                        result = {
                            'url': test_url,
                            'status': status,
                            'content_type': content_type,
                            'response_preview': data,
                            'success': status < 400
                        }
                        validation_results.append(result)
                        print(f"  ✅ {test_url} -> {status} ({content_type})")
                        
                        if status < 400:
                            break  # Found a working endpoint, move on
                            
                except Exception as e:
                    print(f"  ❌ {test_url} -> {str(e)}")
                    continue
        
        # Phase 2: Test actual data endpoints with multiple auth methods
        print("🔍 Phase 2: Testing data endpoints with various auth methods...")
        data_endpoints = [
            '/api/v1/stock/nasdaq/AAPL/short_interest',
            '/api/v1/stocks/AAPL/short-interest',
            '/v1/stock/AAPL/short_interest', 
            '/stock/AAPL/short-interest',
            '/api/stocks/AAPL',
            '/rest/v1/stock/AAPL',
            '/data/stock/AAPL/short'
        ]
        
        # Different auth methods to try - CORRECT METHOD FIRST
        auth_methods = [
            ('CORRECT: Ortex-Api-Key', {'Ortex-Api-Key': ortex_key}),  # THIS IS THE RIGHT ONE!
            ('Ortex-Api-Key Header', {'Ortex-Api-Key': ortex_key}),
            ('Bearer Token', {'Authorization': f'Bearer {ortex_key}'}),
            ('API Key Header', {'API-Key': ortex_key}),
            ('Ortex-API-Key', {'Ortex-API-Key': ortex_key}),
            ('Custom Auth', {'ortex-token': ortex_key}),
            ('X-Ortex-API-Key', {'X-Ortex-API-Key': ortex_key})
        ]
        
        # Test each working domain with each endpoint and auth method
        for domain in ['https://api.ortex.com']:  # Start with primary domain
            for endpoint_path in data_endpoints:
                endpoint_url = f"{domain}{endpoint_path}"
                print(f"  🧪 Testing: {endpoint_url}")
                
                for auth_name, auth_headers in auth_methods:
                    try:
                        headers = {
                            **auth_headers,
                            'Content-Type': 'application/json',
                            'User-Agent': 'Ultimate-Squeeze-Scanner/2.1',
                            'Accept': 'application/json'
                        }
                        
                        req = urllib.request.Request(endpoint_url, headers=headers)
                        with urllib.request.urlopen(req, timeout=15) as response:
                            response_text = response.read().decode()
                            
                            result = {
                                'endpoint': endpoint_path,
                                'url': endpoint_url,
                                'auth_method': auth_name,
                                'status': response.getcode(),
                                'response_length': len(response_text),
                                'has_json': False,
                                'success': False
                            }
                            
                            if response.getcode() == 200:
                                if response_text.strip():
                                    try:
                                        json.loads(response_text)
                                        result['has_json'] = True
                                        result['success'] = True
                                        print(f"    🎉 {endpoint_path} with {auth_name}: SUCCESS!")
                                        validation_results.append(result)
                                        
                                        return {
                                            'valid': True, 
                                            'message': f'API key validated successfully via {endpoint_path} using {auth_name}',
                                            'endpoint': endpoint_url,
                                            'auth_method': auth_name,
                                            'working_endpoints': [result]
                                        }
                                    except json.JSONDecodeError:
                                        result['success'] = False
                                        result['response_preview'] = response_text[:200]
                                        result['content_type'] = response.headers.get('Content-Type', 'unknown')
                                        print(f"    ⚠️ {endpoint_path} with {auth_name}: Non-JSON response")
                                        print(f"       Content-Type: {result['content_type']}")
                                        print(f"       Preview: {response_text[:100]}...")
                                else:
                                    result['success'] = False
                                    result['response_preview'] = "(empty)"
                                    print(f"    ⚠️ {endpoint_path} with {auth_name}: Empty response")
                            
                            validation_results.append(result)
                            
                    except urllib.error.HTTPError as http_e:
                        status = http_e.code
                        
                        # Try to read error response for more details
                        try:
                            error_response = http_e.read().decode()[:300]
                        except:
                            error_response = "Could not read error response"
                        
                        result = {
                            'endpoint': endpoint_path,
                            'url': endpoint_url, 
                            'auth_method': auth_name,
                            'status': status,
                            'success': False,
                            'error_response': error_response
                        }
                        
                        if status == 401:
                            print(f"    ❌ {endpoint_path} with {auth_name}: Unauthorized (401)")
                            result['error'] = 'Unauthorized - Invalid API key'
                        elif status == 403:
                            print(f"    ❌ {endpoint_path} with {auth_name}: Forbidden (403)")
                            result['error'] = 'Forbidden - Check subscription/permissions'  
                            print(f"       Error response: {error_response[:100]}")
                        elif status == 404:
                            print(f"    ❌ {endpoint_path} with {auth_name}: Not Found (404)")
                            result['error'] = 'Endpoint not found'
                        else:
                            print(f"    ❌ {endpoint_path} with {auth_name}: HTTP {status}")
                            result['error'] = f'HTTP {status} error'
                        
                        validation_results.append(result)
                        break  # Don't try other auth methods for this endpoint if we get an auth error
                        
                    except Exception as e:
                        print(f"    ❌ {endpoint_path} with {auth_name}: {str(e)[:50]}")
                        result = {
                            'endpoint': endpoint_path,
                            'url': endpoint_url,
                            'auth_method': auth_name, 
                            'status': 'error',
                            'success': False,
                            'error': str(e)
                        }
                        validation_results.append(result)
                        continue
        
        # Generate detailed failure message
        status_counts = {}
        for result in validation_results:
            status = result.get('status', 'error')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        failure_message = 'API key validation failed. '
        if 401 in status_counts:
            failure_message += f'{status_counts[401]} endpoints returned 401 (Unauthorized). '
        if 403 in status_counts:
            failure_message += f'{status_counts[403]} endpoints returned 403 (Forbidden). '
        if 404 in status_counts:
            failure_message += f'{status_counts[404]} endpoints returned 404 (Not Found). '
            
        return {
            'valid': False,
            'message': failure_message + 'Please check your API key and subscription status.',
            'detailed_results': validation_results,
            'total_tests': len(validation_results)
        }
    
    def debug_ortex_response(self, ortex_key, ticker='AAPL'):
        """Deep dive into what Ortex is actually returning"""
        print(f"🔧 DEEP DIVE: Analyzing Ortex responses for {ticker}")
        
        test_urls = [
            f"https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/short_interest",
            f"https://api.ortex.com/health",
            f"https://api.ortex.com/status",
            f"https://api.ortex.com/api/status"
        ]
        
        debug_results = []
        
        for url in test_urls:
            print(f"📡 Testing URL: {url}")
            
            try:
                req = urllib.request.Request(url)
                req.add_header('Ortex-Api-Key', ortex_key)
                req.add_header('User-Agent', 'Ultimate-Squeeze-Scanner/2.1')
                req.add_header('Accept', 'application/json')
                
                with urllib.request.urlopen(req, timeout=20) as response:
                    # Get all response details
                    status_code = response.getcode()
                    headers = dict(response.headers)
                    content = response.read()
                    
                    # Try to decode content
                    try:
                        content_str = content.decode('utf-8')
                    except:
                        content_str = str(content)[:500]
                    
                    result = {
                        'url': url,
                        'status_code': status_code,
                        'headers': headers,
                        'content_type': headers.get('content-type', 'unknown'),
                        'content_length': len(content),
                        'content_preview': content_str[:500],
                        'is_json': False,
                        'is_html': False,
                        'json_data': None
                    }
                    
                    # Analyze content type
                    if 'json' in result['content_type'].lower():
                        try:
                            result['json_data'] = json.loads(content_str)
                            result['is_json'] = True
                            print(f"  ✅ Valid JSON response!")
                        except:
                            print(f"  ⚠️ Claims JSON but invalid format")
                    elif 'html' in result['content_type'].lower() or content_str.strip().startswith('<!DOCTYPE'):
                        result['is_html'] = True
                        print(f"  ❌ HTML response (likely error page)")
                    
                    debug_results.append(result)
                    
            except urllib.error.HTTPError as e:
                error_content = ""
                try:
                    error_content = e.read().decode('utf-8')[:500]
                except:
                    pass
                    
                result = {
                    'url': url,
                    'status_code': e.code,
                    'error': str(e),
                    'error_content': error_content,
                    'is_json': False,
                    'is_html': 'DOCTYPE' in error_content
                }
                
                print(f"  ❌ HTTP {e.code}: {str(e)}")
                if error_content:
                    print(f"     Error content: {error_content[:100]}...")
                
                debug_results.append(result)
                
            except Exception as e:
                result = {
                    'url': url,
                    'error': str(e),
                    'is_json': False
                }
                print(f"  ❌ Exception: {str(e)}")
                debug_results.append(result)
        
        return debug_results

    def do_GET(self):
        if self.path == '/':
            self.send_html()
        elif self.path == '/api/health':
            self.send_health()
        else:
            self.send_404()
    
    def do_POST(self):
        if self.path == '/api/squeeze/scan':
            self.handle_squeeze_scan()
        elif self.path == '/api/validate-ortex-key':
            self.handle_ortex_validation()
        elif self.path == '/api/debug-ortex-response':
            self.handle_ortex_debug()
        else:
            self.send_404()
    
    def handle_ortex_debug(self):
        """Enhanced debug endpoint for comprehensive Ortex API analysis"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode()) if post_data else {}
            
            ortex_key = data.get('ortex_key', '')
            ticker = data.get('ticker', 'AAPL')
            
            if not ortex_key:
                response = {'error': 'No API key provided'}
            else:
                # Use our comprehensive debug function
                debug_results = self.debug_ortex_response(ortex_key, ticker)
                
                response = {
                    'success': True,
                    'message': f'Completed comprehensive analysis of Ortex API for ticker {ticker}',
                    'api_key_preview': f"{ortex_key[:15]}..." if len(ortex_key) > 15 else ortex_key,
                    'total_tests': len(debug_results),
                    'test_results': debug_results,
                    'summary': {
                        'working_endpoints': len([r for r in debug_results if r.get('is_json', False)]),
                        'html_responses': len([r for r in debug_results if r.get('is_html', False)]),
                        'error_responses': len([r for r in debug_results if 'error' in r]),
                        'total_endpoints_tested': len(debug_results)
                    }
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': f'Debug error: {str(e)}'
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def handle_ortex_validation(self):
        """Handle Ortex API key validation requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode()) if post_data else {}
            
            ortex_key = data.get('ortex_key', '')
            
            if not ortex_key:
                response = {
                    'valid': False,
                    'message': 'No API key provided'
                }
            else:
                response = self.validate_ortex_api_key(ortex_key)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                'valid': False,
                'message': f'Validation error: {str(e)}'
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def get_ortex_data(self, ticker, ortex_key):
        """Get Ortex data using real API endpoints with comprehensive fallbacks"""
        if not ortex_key or len(ortex_key) < 10:
            return None
        
        print(f"🔍 Attempting to get live Ortex data for {ticker}...")
        
        # Try to collect data from multiple specialized endpoints
        ortex_data = {
            'short_interest': 0,
            'days_to_cover': 0, 
            'utilization': 0,
            'cost_to_borrow': 0,
            'shares_on_loan': 0,
            'exchange_reported_si': 0
        }
        
        # CORRECT endpoint strategies based on actual Ortex documentation!
        endpoint_strategies = [
            # ✅ DOCUMENTED endpoint from docs.ortex.com/reference/stock_availability_list
            {
                'name': 'DOCUMENTED: Stock Availability',
                'url': f"https://api.ortex.com/api/v1/stock/{ticker}/availability",
                'priority': 'highest'  # This is confirmed to exist!
            },
            # From your screenshots - these looked like real endpoints
            {
                'name': 'Short Interest Estimates', 
                'url': f"https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/short_interest",
                'priority': 'high'
            },
            {
                'name': 'NYSE Short Interest',
                'url': f"https://api.ortex.com/api/v1/stock/nyse/{ticker}/short_interest", 
                'priority': 'high'
            },
            # Try other potential patterns
            {
                'name': 'Cost to Borrow',
                'url': f"https://api.ortex.com/api/v1/stock/{ticker}/ctb",
                'priority': 'high'
            },
            {
                'name': 'Utilization',
                'url': f"https://api.ortex.com/api/v1/stock/{ticker}/utilization",
                'priority': 'high'
            },
            # Strategy 3: Specialized endpoints (from screenshots)
            {
                'name': 'Short Interest Estimates',
                'url': f"https://api.ortex.com/short-interest/estimates/{ticker}",
                'priority': 'medium'
            },
            {
                'name': 'Short Availability',
                'url': f"https://api.ortex.com/short-interest/availability/{ticker}",
                'priority': 'medium'
            },
            {
                'name': 'Cost to Borrow',
                'url': f"https://api.ortex.com/cost-to-borrow/{ticker}",
                'priority': 'medium'
            },
            # Strategy 4: Alternative domain formats
            {
                'name': 'Public Ortex API',
                'url': f"https://public.ortex.com/api/short-interest/{ticker}",
                'priority': 'low'
            },
            {
                'name': 'Data Ortex API',
                'url': f"https://data.ortex.com/api/v1/short/{ticker}",
                'priority': 'low'
            },
            # Strategy 5: REST-style endpoints
            {
                'name': 'REST Short Interest',
                'url': f"https://api.ortex.com/rest/short-interest/{ticker}",
                'priority': 'low'
            }
        ]
        
        successful_calls = 0
            
        # Real Ortex API endpoints based on actual API documentation
        endpoints_to_try = [
            # Primary Ortex Short Interest endpoints
            f"https://api.ortex.com/short-interest/estimates?symbol={ticker}",
            f"https://api.ortex.com/short-interest/availability?symbol={ticker}", 
            f"https://api.ortex.com/short-interest/days-to-cover?symbol={ticker}",
            f"https://api.ortex.com/cost-to-borrow/new?symbol={ticker}",
            f"https://api.ortex.com/cost-to-borrow/all?symbol={ticker}",
            # Fallback endpoints
            f"https://api.ortex.com/short-interest?ticker={ticker}",
            f"https://ortex-api.com/v1/short-interest/{ticker}"
        ]
        
        # Try each endpoint strategy
        for strategy in endpoint_strategies:
            url = strategy['url']
            strategy_name = strategy['name']
            
            try:
                print(f"  🔍 Trying {strategy_name}...")
                
                # CORRECT authentication method from Ortex documentation!
                auth_methods = [
                    # ✅ CORRECT METHOD from docs.ortex.com
                    {'Ortex-Api-Key': ortex_key},  # THIS IS THE RIGHT ONE!
                    # Fallback methods (in case we need them)
                    {'Authorization': f'Bearer {ortex_key}'},
                    {'Ortex-Api-Key': ortex_key},
                    {'ortex-api-key': ortex_key},
                    {'X-Ortex-Key': ortex_key},
                    {'Authorization': f'Token {ortex_key}'},
                    {'X-Subscription-Key': ortex_key},
                    {'Subscription-Key': ortex_key}
                ]
                
                for i, auth_headers in enumerate(auth_methods):
                    try:
                        headers = {
                            **auth_headers,
                            'Content-Type': 'application/json',
                            'User-Agent': 'Ultimate-Squeeze-Scanner/2.1',
                            'Accept': 'application/json',
                            'Cache-Control': 'no-cache'
                        }
                        
                        # Also try adding API key as URL parameter for some endpoints
                        if i == len(auth_methods) - 1:  # Last attempt, try URL parameter
                            separator = '&' if '?' in url else '?'
                            url_with_key = f"{url}{separator}api_key={ortex_key}"
                            req = urllib.request.Request(url_with_key, headers={'User-Agent': headers['User-Agent']})
                        else:
                            req = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(req, timeout=20) as response:
                            response_text = response.read().decode()
                            
                            if response.status == 200:
                                if response_text.strip():  # Check if response has content
                                    try:
                                        response_data = json.loads(response_text)
                                        
                                        # Parse and merge data based on endpoint type
                                        parsed_data = self.parse_ortex_response_by_type(response_data, ticker, strategy.get('data_type', 'unknown'))
                                        if parsed_data:
                                            successful_calls += 1
                                            print(f"  ✅ {strategy_name} successful! Auth method: {i+1} - Got {strategy.get('data_type', 'data')}")
                                            
                                            # Store data by endpoint type for better organization
                                            endpoint_type = strategy.get('data_type', 'unknown')
                                            gathered_data[endpoint_type] = parsed_data
                                            
                                            # Merge the data (keep best values)
                                            for key, value in parsed_data.items():
                                                if value and value > ortex_data.get(key, 0):
                                                    ortex_data[key] = value
                                            
                                            # Continue to try other endpoints to get comprehensive data
                                            # Don't break early - we want all available data points
                                        else:
                                            print(f"  ⚠️ {strategy_name} returned data but couldn't parse it")
                                    except json.JSONDecodeError as je:
                                        print(f"  ⚠️ {strategy_name} returned non-JSON: {response_text[:100]}")
                                else:
                                    print(f"  ⚠️ {strategy_name} returned empty response (status 200)")
                                    
                            elif response.status == 401:
                                print(f"  ❌ {strategy_name} - Unauthorized (401) - API key may be invalid")
                            elif response.status == 403:
                                print(f"  ❌ {strategy_name} - Forbidden (403) - Check API permissions/subscription")
                            elif response.status == 404:
                                print(f"  ❌ {strategy_name} - Not Found (404) - Wrong endpoint URL")
                            elif response.status == 429:
                                print(f"  ❌ {strategy_name} - Rate Limited (429) - Too many requests")
                            else:
                                print(f"  ⚠️ {strategy_name} - HTTP {response.status}: {response_text[:100]}")
                                
                    except urllib.error.HTTPError as http_e:
                        status_code = http_e.code
                        if status_code == 404:
                            print(f"  ❌ {strategy_name} - 404 Not Found (wrong endpoint)")
                        elif status_code == 401:
                            print(f"  ❌ {strategy_name} - 401 Unauthorized (invalid API key)")
                        elif status_code == 403:
                            print(f"  ❌ {strategy_name} - 403 Forbidden (check permissions)")
                        else:
                            print(f"  ❌ {strategy_name} - HTTP {status_code} error")
                        break  # Don't try other auth methods for HTTP errors
                    except Exception as auth_e:
                        if i == 0:  # Only log on first auth method to avoid spam
                            error_msg = str(auth_e)[:100]
                            if "Name or service not known" in error_msg:
                                print(f"  ❌ {strategy_name} - Invalid domain/URL")
                            else:
                                print(f"  ⚠️ {strategy_name} error: {error_msg}")
                        continue  # Try next auth method
                        
            except Exception as e:
                print(f"  ❌ {strategy_name} failed: {str(e)[:100]}")
                continue  # Try next strategy
                
        # Check if we got any meaningful data from the API calls
        if successful_calls > 0 and ortex_data['short_interest'] > 0:
            print(f"✅ Successfully retrieved Ortex data for {ticker} from {successful_calls} endpoint(s)")
            return ortex_data
        elif successful_calls > 0:
            print(f"⚠️ Partial Ortex data retrieved for {ticker} from {successful_calls} endpoint(s)")
            return ortex_data
        else:
            print(f"❌ All Ortex API attempts failed for {ticker}, using enhanced fallback data")
            return self.get_ortex_web_fallback(ticker)
        
    def parse_ortex_response_by_type(self, data, ticker, endpoint_type):
        """Parse Ortex API responses based on specific endpoint type"""
        try:
            result = {}
            
            # Handle different endpoint types based on your API screenshots
            if endpoint_type == 'short_interest':
                # Short Interest Estimates endpoint
                if isinstance(data, dict):
                    result['short_interest'] = data.get('si_percent_ff', 0) or data.get('percent_of_freefloat', 0) or data.get('short_interest', 0)
                    result['shares_on_loan'] = data.get('shares_on_loan', 0) or data.get('short_shares', 0)
                    result['exchange_reported_si'] = data.get('exchange_si', 0) or data.get('official_si', 0)
                
            elif endpoint_type == 'availability':
                # Short Availability endpoint
                if isinstance(data, dict):
                    result['utilization'] = data.get('utilization_rate', 0) or data.get('utilization', 0) 
                    result['free_float'] = data.get('freefloat_on_loan', 0) or data.get('free_float', 0)
                    
            elif endpoint_type == 'days_to_cover':
                # Days to Cover endpoint
                if isinstance(data, (int, float)):
                    result['days_to_cover'] = float(data)
                elif isinstance(data, dict):
                    result['days_to_cover'] = data.get('days_to_cover', 0) or data.get('dtc', 0) or data.get('value', 0)
                    
            elif endpoint_type in ['ctb_new', 'ctb_all']:
                # Cost to Borrow endpoints
                if isinstance(data, (int, float)):
                    result['cost_to_borrow'] = float(data)
                elif isinstance(data, dict):
                    result['cost_to_borrow'] = data.get('cost_to_borrow', 0) or data.get('ctb', 0) or data.get('rate', 0) or data.get('average_rate', 0)
                    
            elif endpoint_type == 'shares_outstanding':
                # Shares Outstanding endpoint
                if isinstance(data, dict):
                    result['shares_outstanding'] = data.get('shares_outstanding', 0) or data.get('outstanding_shares', 0)
                    result['float_shares'] = data.get('float_shares', 0) or data.get('free_float', 0)
                    
            elif endpoint_type == 'stock_scores':
                # Stock Scores endpoint - might contain composite data
                if isinstance(data, dict):
                    result['squeeze_score'] = data.get('squeeze_score', 0) or data.get('short_squeeze_score', 0)
                    result['momentum_score'] = data.get('momentum_score', 0)
                    
            # Fallback: try to parse any numeric data we can find
            if not result and isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float)) and value > 0:
                        # Map common field names to our standard fields
                        if any(term in key.lower() for term in ['short', 'si']):
                            result['short_interest'] = float(value)
                        elif any(term in key.lower() for term in ['util', 'utiliz']):
                            result['utilization'] = float(value)
                        elif any(term in key.lower() for term in ['ctb', 'borrow', 'cost']):
                            result['cost_to_borrow'] = float(value)
                        elif any(term in key.lower() for term in ['dtc', 'days', 'cover']):
                            result['days_to_cover'] = float(value)
            
            # Return result if we got any meaningful data
            if result and any(v > 0 for v in result.values()):
                print(f"✅ Parsed {endpoint_type} data for {ticker}: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Error parsing {endpoint_type} response for {ticker}: {e}")
            
        return None

    def parse_ortex_response(self, data, ticker):
        """Parse Ortex API response formats based on real endpoint structures"""
        try:
            ortex_result = {
                'short_interest': 0,
                'days_to_cover': 0,
                'utilization': 0,
                'cost_to_borrow': 0,
                'shares_on_loan': 0,
                'exchange_reported_si': 0,
                'free_float': 0
            }
            
            # Handle different possible response structures from Ortex API
            if isinstance(data, dict):
                # Short Interest Estimates response
                if 'estimates' in data or 'short_interest_estimates' in data:
                    estimates = data.get('estimates') or data.get('short_interest_estimates', {})
                    if isinstance(estimates, dict):
                        ortex_result['short_interest'] = estimates.get('percent_of_freefloat', 0) or estimates.get('si_percent', 0)
                        ortex_result['shares_on_loan'] = estimates.get('shares_on_loan', 0) or estimates.get('short_shares', 0)
                
                # Short Availability response  
                if 'availability' in data or 'short_availability' in data:
                    availability = data.get('availability') or data.get('short_availability', {})
                    if isinstance(availability, dict):
                        ortex_result['utilization'] = availability.get('utilization_rate', 0) or availability.get('utilization', 0)
                        ortex_result['free_float'] = availability.get('freefloat_on_loan', 0)
                
                # Days to Cover response
                if 'days_to_cover' in data or 'dtc' in data:
                    dtc_data = data.get('days_to_cover') or data.get('dtc')
                    if isinstance(dtc_data, (int, float)):
                        ortex_result['days_to_cover'] = dtc_data
                    elif isinstance(dtc_data, dict):
                        ortex_result['days_to_cover'] = dtc_data.get('value', 0) or dtc_data.get('days', 0)
                
                # Cost to Borrow response
                if 'cost_to_borrow' in data or 'ctb' in data or 'borrow_rate' in data:
                    ctb_data = data.get('cost_to_borrow') or data.get('ctb') or data.get('borrow_rate')
                    if isinstance(ctb_data, (int, float)):
                        ortex_result['cost_to_borrow'] = ctb_data
                    elif isinstance(ctb_data, dict):
                        ortex_result['cost_to_borrow'] = ctb_data.get('rate', 0) or ctb_data.get('average_rate', 0)
                
                # Direct field mapping (for simpler response formats)
                field_mappings = {
                    'short_interest': ['short_interest', 'shortInterest', 'si_percent', 'short_interest_percent'],
                    'days_to_cover': ['days_to_cover', 'daysToCover', 'dtc'],
                    'utilization': ['utilization', 'utilization_rate', 'util', 'utilization_percent'],
                    'cost_to_borrow': ['cost_to_borrow', 'costToBorrow', 'ctb', 'borrow_rate', 'avg_borrow_rate'],
                    'shares_on_loan': ['shares_on_loan', 'sharesOnLoan', 'short_shares', 'borrowed_shares'],
                    'exchange_reported_si': ['exchange_si', 'exchangeReportedSI', 'official_si', 'exchange_short_interest']
                }
                
                for result_key, possible_keys in field_mappings.items():
                    for key in possible_keys:
                        if key in data and data[key] is not None:
                            ortex_result[result_key] = float(data[key])
                            break
                
                # Handle nested structures
                if 'data' in data and isinstance(data['data'], dict):
                    nested_result = self.parse_ortex_response(data['data'], ticker)
                    if nested_result:
                        for key, value in nested_result.items():
                            if value > 0:  # Only update if we got a real value
                                ortex_result[key] = value
                
                # Handle array results
                if 'results' in data and isinstance(data['results'], list) and data['results']:
                    array_result = self.parse_ortex_response(data['results'][0], ticker)
                    if array_result:
                        for key, value in array_result.items():
                            if value > 0:
                                ortex_result[key] = value
                                
            elif isinstance(data, list) and data:
                return self.parse_ortex_response(data[0], ticker)
            
            # Return result if we got any meaningful data
            if any(ortex_result[key] > 0 for key in ['short_interest', 'utilization', 'cost_to_borrow', 'days_to_cover']):
                print(f"✅ Successfully parsed Ortex data for {ticker}: SI={ortex_result['short_interest']}%, Util={ortex_result['utilization']}%")
                return ortex_result
                
        except Exception as e:
            print(f"❌ Error parsing Ortex response for {ticker}: {e}")
            
        return None
    
    def get_ortex_web_fallback(self, ticker):
        """Fallback method using web scraping (for demo purposes)"""
        try:
            # This would be a fallback web scraping method
            # For now, return enhanced mock data that could represent real Ortex data
            print(f"⚠️  Using enhanced mock data for {ticker} (Ortex API key not working)")
            
            # Enhanced realistic mock data based on actual market conditions
            enhanced_mock = {
                'GME': {'si': 22.4, 'dtc': 4.1, 'util': 89.2, 'ctb': 12.8},
                'AMC': {'si': 18.7, 'dtc': 3.8, 'util': 82.1, 'ctb': 8.9},
                'BBBY': {'si': 45.2, 'dtc': 8.2, 'util': 98.7, 'ctb': 35.4},
                'AAPL': {'si': 1.2, 'dtc': 0.8, 'util': 25.1, 'ctb': 0.5},
                'TSLA': {'si': 15.3, 'dtc': 2.9, 'util': 76.4, 'ctb': 7.2},
                'NVDA': {'si': 3.1, 'dtc': 1.1, 'util': 34.2, 'ctb': 1.8}
            }
            
            if ticker in enhanced_mock:
                mock = enhanced_mock[ticker]
                return {
                    'short_interest': mock['si'],
                    'days_to_cover': mock['dtc'],
                    'utilization': mock['util'],
                    'cost_to_borrow': mock['ctb'],
                    'shares_on_loan': mock['si'] * 1000000,  # Estimate
                    'exchange_reported_si': mock['si'] * 0.85  # Estimate
                }
            
            # Return default for unknown tickers
            return {
                'short_interest': 8.5,
                'days_to_cover': 2.1,
                'utilization': 65.3,
                'cost_to_borrow': 4.7,
                'shares_on_loan': 8500000,
                'exchange_reported_si': 7.2
            }
            
        except Exception as e:
            print(f"Fallback data error for {ticker}: {e}")
            return None
    
    def get_stock_price_data(self, ticker):
        """Get current stock price from multiple free APIs with fallbacks"""
        # Try multiple APIs for better reliability
        apis_to_try = [
            ('Yahoo Finance', self.get_yahoo_price),
            ('Alpha Vantage (Free)', self.get_alphavantage_price),
            ('Financial Modeling Prep (Free)', self.get_fmp_price)
        ]
        
        for api_name, api_func in apis_to_try:
            try:
                result = api_func(ticker)
                if result:
                    print(f"✅ Price data from {api_name} for {ticker}")
                    return result
            except Exception as e:
                print(f"⚠️  {api_name} failed for {ticker}: {e}")
                continue
        
        print(f"⚠️  All price APIs failed for {ticker}, using mock data")
        return self.get_mock_price_data(ticker)
    
    def get_yahoo_price(self, ticker):
        """Get price from Yahoo Finance API"""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                
                result = data.get('chart', {}).get('result', [])
                if result:
                    meta = result[0].get('meta', {})
                    current_price = meta.get('regularMarketPrice', 0)
                    previous_close = meta.get('previousClose', current_price)
                    volume = meta.get('regularMarketVolume', 0)
                    
                    price_change_percent = 0
                    if previous_close > 0:
                        price_change_percent = ((current_price - previous_close) / previous_close) * 100
                    
                    return {
                        'current_price': round(current_price, 2),
                        'price_change': round(price_change_percent, 2),
                        'volume': volume,
                        'previous_close': previous_close,
                        'source': 'yahoo_finance'
                    }
        return None
    
    def get_alphavantage_price(self, ticker):
        """Get price from Alpha Vantage (free tier)"""
        # Free API key (demo) - users should replace with their own
        api_key = "demo"  
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
        
        headers = {'User-Agent': 'Ultimate-Squeeze-Scanner/2.0'}
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                
                quote = data.get('Global Quote', {})
                if quote:
                    current_price = float(quote.get('05. price', 0))
                    previous_close = float(quote.get('08. previous close', current_price))
                    volume = int(quote.get('06. volume', 0))
                    
                    price_change_percent = 0
                    if previous_close > 0:
                        price_change_percent = ((current_price - previous_close) / previous_close) * 100
                    
                    return {
                        'current_price': round(current_price, 2),
                        'price_change': round(price_change_percent, 2),
                        'volume': volume,
                        'previous_close': previous_close,
                        'source': 'alpha_vantage'
                    }
        return None
    
    def get_fmp_price(self, ticker):
        """Get price from Financial Modeling Prep (free tier)"""
        url = f"https://financialmodelingprep.com/api/v3/quote-short/{ticker}?apikey=demo"
        
        headers = {'User-Agent': 'Ultimate-Squeeze-Scanner/2.0'}
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                
                if isinstance(data, list) and data:
                    quote = data[0]
                    current_price = float(quote.get('price', 0))
                    previous_close = float(quote.get('previousClose', current_price))
                    volume = int(quote.get('volume', 0))
                    
                    price_change_percent = 0
                    if previous_close > 0:
                        price_change_percent = ((current_price - previous_close) / previous_close) * 100
                    
                    return {
                        'current_price': round(current_price, 2),
                        'price_change': round(price_change_percent, 2),
                        'volume': volume,
                        'previous_close': previous_close,
                        'source': 'fmp'
                    }
        return None
    
    def get_mock_price_data(self, ticker):
        """Enhanced mock price data as fallback"""
        mock_prices = {
            'GME': {'price': 18.75, 'change': 2.3, 'volume': 15420000},
            'AMC': {'price': 4.82, 'change': -1.2, 'volume': 28750000},
            'BBBY': {'price': 0.35, 'change': 8.7, 'volume': 45820000},
            'AAPL': {'price': 178.90, 'change': 0.8, 'volume': 67890000},
            'TSLA': {'price': 234.56, 'change': 3.2, 'volume': 45670000},
            'NVDA': {'price': 456.78, 'change': 2.1, 'volume': 34560000},
            'SPY': {'price': 428.45, 'change': 0.3, 'volume': 89750000},
            'QQQ': {'price': 367.23, 'change': 0.8, 'volume': 45670000}
        }
        
        if ticker in mock_prices:
            mock = mock_prices[ticker]
        else:
            # Generate realistic mock data for unknown tickers
            import random
            mock = {
                'price': round(random.uniform(5, 150), 2),
                'change': round(random.uniform(-5, 5), 2),
                'volume': random.randint(1000000, 50000000)
            }
        
        previous_close = round(mock['price'] / (1 + mock['change']/100), 2)
        
        return {
            'current_price': mock['price'],
            'price_change': mock['change'],
            'volume': mock['volume'],
            'previous_close': previous_close,
            'source': 'mock_data'
        }
    
    def calculate_squeeze_score(self, ortex_data, price_data):
        """Enhanced squeeze score calculation with professional-grade algorithm"""
        if not ortex_data:
            return 50  # Default score
        
        score = 0
        details = {'breakdown': {}, 'risk_factors': []}
        
        # 1. Short Interest Analysis (0-35 points) - Most Important
        si = ortex_data.get('short_interest', 0)
        si_score = 0
        if si >= 40:
            si_score = 35
            details['risk_factors'].append('EXTREME_SHORT_INTEREST')
        elif si >= 30:
            si_score = 30
            details['risk_factors'].append('VERY_HIGH_SHORT_INTEREST')
        elif si >= 20:
            si_score = 25
            details['risk_factors'].append('HIGH_SHORT_INTEREST')
        elif si >= 15:
            si_score = 15
        elif si >= 10:
            si_score = 8
        elif si >= 5:
            si_score = 3
        
        score += si_score
        details['breakdown']['short_interest'] = si_score
        
        # 2. Utilization Rate (0-25 points)
        util = ortex_data.get('utilization', 0)
        util_score = 0
        if util >= 98:
            util_score = 25
            details['risk_factors'].append('MAXED_UTILIZATION')
        elif util >= 95:
            util_score = 22
            details['risk_factors'].append('CRITICAL_UTILIZATION')
        elif util >= 90:
            util_score = 20
        elif util >= 85:
            util_score = 18
        elif util >= 80:
            util_score = 15
        elif util >= 75:
            util_score = 12
        elif util >= 60:
            util_score = 8
        elif util >= 40:
            util_score = 4
        
        score += util_score
        details['breakdown']['utilization'] = util_score
        
        # 3. Cost to Borrow (0-25 points)
        ctb = ortex_data.get('cost_to_borrow', 0)
        ctb_score = 0
        if ctb >= 50:
            ctb_score = 25
            details['risk_factors'].append('EXTREME_BORROW_COST')
        elif ctb >= 30:
            ctb_score = 22
            details['risk_factors'].append('VERY_HIGH_BORROW_COST')
        elif ctb >= 20:
            ctb_score = 20
        elif ctb >= 15:
            ctb_score = 18
        elif ctb >= 10:
            ctb_score = 15
        elif ctb >= 8:
            ctb_score = 12
        elif ctb >= 5:
            ctb_score = 10
        elif ctb >= 3:
            ctb_score = 6
        elif ctb >= 1:
            ctb_score = 3
        
        score += ctb_score
        details['breakdown']['cost_to_borrow'] = ctb_score
        
        # 4. Days to Cover (0-15 points)
        dtc = ortex_data.get('days_to_cover', 0)
        dtc_score = 0
        if dtc >= 10:
            dtc_score = 15
            details['risk_factors'].append('EXTREME_DAYS_TO_COVER')
        elif dtc >= 7:
            dtc_score = 13
        elif dtc >= 5:
            dtc_score = 11
        elif dtc >= 4:
            dtc_score = 10
        elif dtc >= 3:
            dtc_score = 8
        elif dtc >= 2:
            dtc_score = 5
        elif dtc >= 1:
            dtc_score = 2
        
        score += dtc_score
        details['breakdown']['days_to_cover'] = dtc_score
        
        # 5. Price Action Momentum Bonus (0-10 points)
        if price_data:
            price_change = price_data.get('price_change', 0)
            volume = price_data.get('volume', 0)
            
            momentum_score = 0
            if price_change > 10:  # Strong upward momentum
                momentum_score = 10
                details['risk_factors'].append('STRONG_UPWARD_MOMENTUM')
            elif price_change > 5:
                momentum_score = 7
            elif price_change > 2:
                momentum_score = 4
            elif price_change > 0:
                momentum_score = 2
            elif price_change < -10:  # Strong downward pressure could indicate covering
                momentum_score = -5
                
            # Volume amplification
            if volume > 50000000:  # High volume
                momentum_score += 2
                details['risk_factors'].append('HIGH_VOLUME')
            elif volume > 20000000:
                momentum_score += 1
                
            score += max(-5, min(10, momentum_score))  # Cap between -5 and 10
            details['breakdown']['momentum'] = momentum_score
        
        # 6. Composite Risk Multiplier
        # If multiple extreme factors are present, apply multiplier
        extreme_factors = sum(1 for factor in ['EXTREME_SHORT_INTEREST', 'MAXED_UTILIZATION', 'EXTREME_BORROW_COST', 'EXTREME_DAYS_TO_COVER'] if factor in details['risk_factors'])
        
        if extreme_factors >= 3:
            score = min(100, score * 1.1)  # 10% bonus for triple threat
            details['risk_factors'].append('TRIPLE_THREAT_MULTIPLIER')
        elif extreme_factors >= 2:
            score = min(100, score * 1.05)  # 5% bonus for double threat
            details['risk_factors'].append('DOUBLE_THREAT_MULTIPLIER')
        
        final_score = min(100, max(0, score))  # Ensure score is between 0-100
        details['final_score'] = final_score
        
        return final_score, details
    
    def get_squeeze_type(self, score):
        """Determine squeeze risk level based on score"""
        if score >= 80:
            return "EXTREME SQUEEZE RISK"
        elif score >= 60:
            return "High Squeeze Risk"
        elif score >= 40:
            return "Moderate Squeeze Risk"
        else:
            return "Low Squeeze Risk"

    def send_html(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 Ultimate Squeeze Scanner</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            color: #ff6b6b;
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
        }
        .header p {
            color: #a0a0b0;
            font-size: 1.2rem;
        }
        .form-section {
            background: #1a1a2e;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 1px solid #3a3a4e;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #a0a0b0;
            font-weight: bold;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            background: #2a2a3e;
            border: 2px solid #3a3a4e;
            border-radius: 8px;
            color: #e0e0e0;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #ff6b6b;
        }
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        button {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            flex: 1;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        }
        .results {
            background: #1a1a2e;
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #3a3a4e;
            margin-top: 30px;
        }
        .result-item {
            padding: 20px;
            margin: 15px 0;
            background: #2a2a3e;
            border-radius: 10px;
            border-left: 5px solid #ff6b6b;
            transition: transform 0.3s;
        }
        .result-item:hover {
            transform: translateX(5px);
        }
        .score-extreme { border-left-color: #dc3545; }
        .score-high { border-left-color: #ffc107; }
        .score-medium { border-left-color: #17a2b8; }
        .score-low { border-left-color: #28a745; }
        .loading {
            text-align: center;
            color: #ff6b6b;
            font-size: 20px;
            padding: 40px;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }
        .status-healthy { background: #28a745; }
        .status-error { background: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 ULTIMATE SQUEEZE SCANNER</h1>
            <p>Professional short squeeze detection with live Ortex API + Yahoo Finance integration</p>
        </div>

        <div class="form-section">
            <h2>🔑 Configuration</h2>
            <div class="form-group">
                <label for="ortexKey">🔑 Ortex API Key (For Live Short Interest Data):</label>
                <input type="password" id="ortexKey" placeholder="Enter your Ortex API key for real-time short interest data">
                <div style="margin-top: 8px; font-size: 0.9rem; color: #a0a0b0;">
                    💡 <strong>Get Live Data:</strong> Sign up at <a href="https://www.ortex.com" target="_blank" style="color: #ff6b6b;">ortex.com</a> for API access
                    <br>🔧 <strong>Server Setup:</strong> Set ORTEX_API_KEY environment variable for automatic use
                    <br>📊 Without API key: Uses enhanced mock data with real-time prices from Yahoo Finance
                </div>
            </div>

            <div class="form-group">
                <label for="tickerPreset">🎯 Quick Select:</label>
                <select id="tickerPreset" onchange="loadTickerPreset()" style="margin-bottom: 10px;">
                    <option value="top_squeeze">🔥 Top Squeeze Plays (25)</option>
                    <option value="meme_legends">🚀 Meme Legends (5)</option>
                    <option value="high_si">📊 High Short Interest (15)</option>
                    <option value="biotech">🧬 Biotech & Health (8)</option>
                    <option value="ev_tech">⚡ EV & Tech (10)</option>
                    <option value="spac_plays">💫 SPAC & Growth (8)</option>
                    <option value="penny_squeeze">💰 Penny Squeezes (10)</option>
                    <option value="reddit_favorites">🦍 Reddit Favorites (12)</option>
                    <option value="institutional_targets">🏛️ Institutional Targets (10)</option>
                    <option value="crypto_related">₿ Crypto Related (6)</option>
                    <option value="ai_machine_learning">🤖 AI & ML Stocks (8)</option>
                    <option value="all_tickers">🌍 All Available (100+)</option>
                    <option value="custom">✏️ Custom</option>
                </select>
                
                <label for="tickers">Squeeze Targets:</label>
                <textarea id="tickers" rows="4" placeholder="Enter tickers separated by commas">GME, AMC, BBBY, RDBX, MULN, TSLA, COIN, NVDA, PLTR, NIO, RIVN, HOOD, ROKU, PTON, C3AI, TLRY, NOK, RIOT, MARA, ENDP</textarea>
            </div>

            <div class="button-group">
                <button onclick="runSqueezeScan()">🔥 RUN SQUEEZE SCAN</button>
                <button onclick="validateOrtexKey()">🔑 VALIDATE ORTEX KEY</button>
                <button onclick="debugOrtexResponse()">🔍 DEBUG ORTEX RESPONSE</button>
                <button onclick="runHealthCheck()">📊 API HEALTH CHECK</button>
            </div>
        </div>

        <div id="results"></div>
    </div>

    <script>
        // Auto-run health check on page load
        window.onload = function() {
            runHealthCheck();
        };

        function loadTickerPreset() {
            const preset = document.getElementById('tickerPreset').value;
            const tickerTextarea = document.getElementById('tickers');
            
            const presets = {
                'top_squeeze': 'GME, AMC, BBBY, ATER, SPRT, DWAC, PHUN, SAVA, KOSS, APRN, UPST, NKLA, OPAD, BGFV, VXRT, BYND, CLOV, MRIN, PROG, IRNT, RDBX, MULN, ENDP, TLRY, WKHS',
                'meme_legends': 'GME, AMC, BBBY, KOSS, NOK',
                'high_si': 'BBBY, DWAC, SAVA, PHUN, ATER, SPRT, APRN, KOSS, BGFV, NKLA, RDBX, MULN, ENDP, CANO, NVAX',
                'biotech': 'SAVA, VXRT, CLOV, BYND, NVAX, OCGN, SRNE, SESN',
                'ev_tech': 'NKLA, RIDE, WKHS, GOEV, MULN, ARVL, LCID, RIVN, XPEV, NIO',
                'spac_plays': 'DWAC, PHUN, BKKT, MARK, CCIV, PSTH, IPOF, CLOV',
                'penny_squeeze': 'BBBY, SNDL, NAKD, EXPR, WISH, RDBX, MULN, ENDP, CANO, GNUS',
                'reddit_favorites': 'GME, AMC, BBBY, PLTR, NIO, TLRY, SNDL, NOK, BB, CLOV, WISH, RKT',
                'institutional_targets': 'TSLA, AAPL, NVDA, NFLX, SHOP, ROKU, PELOTON, ZM, HOOD, COIN',
                'crypto_related': 'COIN, RIOT, MARA, HUT, BITF, SI',
                'ai_machine_learning': 'NVDA, AMD, PLTR, C3AI, UPST, SNOW, NET, DDOG',
                'all_tickers': 'GME, AMC, BBBY, ATER, SPRT, IRNT, OPAD, MRIN, BGFV, PROG, NKLA, RIDE, WKHS, GOEV, SAVA, VXRT, CLOV, BYND, APRN, UPST, SKLZ, WISH, GEVO, KOSS, NAKD, EXPR, DWAC, PHUN, BKKT, MARK, SNDL, CCIV, PSTH, RDBX, MULN, ENDP, CANO, GNUS, NVAX, OCGN, SRNE, SESN, ARVL, LCID, RIVN, XPEV, NIO, IPOF, PLTR, TLRY, NOK, BB, RKT, TSLA, AAPL, NVDA, NFLX, SHOP, ROKU, PTON, ZM, HOOD, COIN, RIOT, MARA, HUT, BITF, SI, AMD, C3AI, AI, SNOW, NET, DDOG, SPCE, SOFI, SQ, PYPL, UBER, LYFT, ABNB, DOCU, CRM, OKTA, TWLO, ESTC, MDB, CRWD, ZS, DKNG, PENN, MGNI, TTD, CROX, LULU, ETSY, W, CHWY, TWTR, SNAP, PINS, MTCH, BMBL, RBLX, PATH, AFRM, OPEN'
            };
            
            if (preset !== 'custom' && presets[preset]) {
                tickerTextarea.value = presets[preset];
            }
        }

        async function runHealthCheck() {
            showLoading('Testing API connection...');
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                showHealthResult(data);
            } catch (error) {
                showError('❌ Health check failed: ' + error.message);
            }
        }

        async function validateOrtexKey() {
            const ortexKey = document.getElementById('ortexKey').value.trim();
            
            if (!ortexKey) {
                showError('❌ Please enter an Ortex API key to validate');
                return;
            }

            showLoading('🔑 Validating Ortex API key...');

            try {
                const response = await fetch('/api/validate-ortex-key', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ortex_key: ortexKey
                    })
                });

                const data = await response.json();
                showOrtexValidationResult(data);
            } catch (error) {
                showError('❌ Validation failed: ' + error.message);
            }
        }

        async function debugOrtexResponse() {
            const ortexKey = document.getElementById('ortexKey').value.trim();
            
            if (!ortexKey) {
                showError('❌ Please enter an Ortex API key to debug');
                return;
            }

            showLoading('🔍 Debugging Ortex API response...');

            try {
                const response = await fetch('/api/debug-ortex-response', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ortex_key: ortexKey,
                        test_url: 'https://api.ortex.com/api/v1/stock/nasdaq/AAPL/short_interest'
                    })
                });

                const data = await response.json();
                showOrtexDebugResult(data);
            } catch (error) {
                showError('❌ Debug failed: ' + error.message);
            }
        }

        async function runSqueezeScan() {
            const ortexKey = document.getElementById('ortexKey').value.trim();
            const tickerText = document.getElementById('tickers').value.trim();
            
            if (!tickerText) {
                showError('❌ Please enter at least one ticker symbol');
                return;
            }

            const tickers = tickerText.split(',').map(t => t.trim().toUpperCase()).filter(t => t);
            
            showLoading('🔥 Scanning ' + tickers.length + ' tickers for squeeze opportunities...');

            try {
                const response = await fetch('/api/squeeze/scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ortex_key: ortexKey,
                        tickers: tickers
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    showSqueezeResults(data.results, data.message);
                } else {
                    showError('❌ ' + (data.message || 'Scan failed'));
                }
            } catch (error) {
                showError('❌ Network error: ' + error.message);
            }
        }

        function showLoading(message) {
            document.getElementById('results').innerHTML = `
                <div class="results">
                    <div class="loading">
                        <div style="font-size: 30px; margin-bottom: 10px;">⚡</div>
                        ${message}
                    </div>
                </div>`;
        }

        function showError(message) {
            document.getElementById('results').innerHTML = `
                <div class="results">
                    <h3>⚠️ Error</h3>
                    <div class="result-item status-error">
                        ${message}
                    </div>
                </div>`;
        }

        function showHealthResult(data) {
            const statusClass = data.status === 'healthy' ? 'status-healthy' : 'status-error';
            const ortexEnvStatus = data.ortex_env_configured ? 
                '<span style="color: #28a745;">✅ Configured</span>' : 
                '<span style="color: #ffc107;">⚠️ Not Set</span>';
            
            document.getElementById('results').innerHTML = `
                <div class="results">
                    <h3>🔍 API Health Check</h3>
                    <div class="result-item">
                        <strong>Status:</strong> <span class="status-badge ${statusClass}">${data.status.toUpperCase()}</span><br>
                        <strong>Message:</strong> ${data.message}<br>
                        <strong>Ortex Environment Variable:</strong> ${ortexEnvStatus}<br>
                        <strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}
                        ${data.ortex_env_configured ? 
                            '<br><br><div style="color: #28a745; font-size: 0.9rem;">🎉 <strong>Server-side Ortex API key detected!</strong><br>You can leave the API key field above empty - live data will be used automatically.</div>' :
                            '<br><br><div style="color: #a0a0b0; font-size: 0.9rem;">💡 <strong>Pro Tip:</strong> Set ORTEX_API_KEY environment variable in Vercel for automatic live data without entering keys in the UI.</div>'
                        }
                    </div>
                </div>`;
        }

        function showOrtexValidationResult(data) {
            const statusClass = data.valid ? 'status-healthy' : 'status-error';
            const statusIcon = data.valid ? '✅' : '❌';
            const statusText = data.valid ? 'VALID' : 'INVALID';
            
            document.getElementById('results').innerHTML = `
                <div class="results">
                    <h3>🔑 Ortex API Key Validation</h3>
                    <div class="result-item">
                        <strong>Status:</strong> <span class="status-badge ${statusClass}">${statusIcon} ${statusText}</span><br>
                        <strong>Message:</strong> ${data.message}<br>
                        ${data.endpoint ? `<strong>Test Endpoint:</strong> ${data.endpoint}<br>` : ''}
                        <strong>Timestamp:</strong> ${new Date().toLocaleString()}
                        ${data.valid ? 
                            '<br><br><div style="color: #28a745; font-size: 0.9rem;">🎉 <strong>Excellent!</strong> Your Ortex API key is valid and working. You can now run squeeze scans to get live data!</div>' :
                            '<br><br><div style="color: #ff6b6b; font-size: 0.9rem;">⚠️ <strong>API Key Issue:</strong> Please check your Ortex API key and make sure you have the necessary permissions for short interest data access.</div>'
                        }
                    </div>
                </div>`;
        }

        function showOrtexDebugResult(data) {
            const statusClass = data.success ? 'status-healthy' : 'status-error';
            const statusIcon = data.success ? '✅' : '❌';
            
            let debugInfo = '';
            if (data.success) {
                debugInfo = `
                    <strong>URL:</strong> ${data.url}<br>
                    <strong>HTTP Status:</strong> ${data.status}<br>
                    <strong>Content-Type:</strong> ${data.content_type}<br>
                    <strong>Response Length:</strong> ${data.response_length} characters<br>
                    <strong>Is JSON:</strong> ${data.is_json ? '✅ Yes' : '❌ No'}<br>
                    <strong>Is HTML:</strong> ${data.is_html ? '✅ Yes' : '❌ No'}<br>
                    <strong>Is XML:</strong> ${data.is_xml ? '✅ Yes' : '❌ No'}<br>
                    <br>
                    <strong>First 100 Characters:</strong><br>
                    <div style="background: #2a2a3e; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.8rem; white-space: pre-wrap; max-height: 200px; overflow-y: auto;">
${data.first_100_chars || '(empty)'}
                    </div>
                    ${data.response_length > 100 ? `
                    <br>
                    <details>
                        <summary>Full Response (Click to expand)</summary>
                        <div style="background: #2a2a3e; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.7rem; white-space: pre-wrap; max-height: 400px; overflow-y: auto; margin-top: 10px;">
${data.response_text}
                        </div>
                    </details>
                    ` : ''}
                `;
            } else {
                debugInfo = `
                    <strong>Error:</strong> ${data.error}<br>
                    ${data.url ? `<strong>URL:</strong> ${data.url}<br>` : ''}
                    ${data.status ? `<strong>HTTP Status:</strong> ${data.status}<br>` : ''}
                    ${data.response_text ? `
                    <br><strong>Error Response:</strong><br>
                    <div style="background: #2a2a3e; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.8rem; white-space: pre-wrap;">
${data.response_text}
                    </div>
                    ` : ''}
                `;
            }
            
            document.getElementById('results').innerHTML = `
                <div class="results">
                    <h3>🔍 Ortex API Debug Results</h3>
                    <div class="result-item">
                        <strong>Status:</strong> <span class="status-badge ${statusClass}">${statusIcon} ${data.success ? 'SUCCESS' : 'FAILED'}</span><br>
                        ${debugInfo}
                        <br><strong>Timestamp:</strong> ${new Date().toLocaleString()}
                    </div>
                </div>`;
        }

        function showSqueezeResults(results, message) {
            if (!results || results.length === 0) {
                document.getElementById('results').innerHTML = `
                    <div class="results">
                        <h3>🎯 Squeeze Scan Results</h3>
                        <div class="result-item">No squeeze candidates found. Try different tickers or lower criteria.</div>
                    </div>`;
                return;
            }

            let html = `<div class="results">
                <h3>🎯 Professional Squeeze Analysis Results</h3>
                <p><strong>${message}</strong></p>
                
                <!-- Summary Statistics -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    <div style="background: #2a2a3e; padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5rem; color: #ff6b6b; font-weight: bold;">${results.length}</div>
                        <div style="color: #a0a0b0; font-size: 0.9rem;">Total Candidates</div>
                    </div>
                    <div style="background: #2a2a3e; padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5rem; color: #00ff88; font-weight: bold;">${results.filter(r => r.squeeze_score >= 80).length}</div>
                        <div style="color: #a0a0b0; font-size: 0.9rem;">Extreme Risk</div>
                    </div>
                    <div style="background: #2a2a3e; padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5rem; color: #ffc107; font-weight: bold;">${results.filter(r => r.squeeze_score >= 60 && r.squeeze_score < 80).length}</div>
                        <div style="color: #a0a0b0; font-size: 0.9rem;">High Risk</div>
                    </div>
                    <div style="background: #2a2a3e; padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5rem; color: #17a2b8; font-weight: bold;">${Math.round(results.reduce((sum, r) => sum + r.squeeze_score, 0) / results.length)}</div>
                        <div style="color: #a0a0b0; font-size: 0.9rem;">Avg Score</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px; padding: 15px; background: #2a2a3e; border-radius: 8px; font-size: 0.9rem;">
                    <strong>📋 Data Sources & Professional Features:</strong><br>
                    <span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; margin: 0 5px;">🔴 LIVE</span> Real Ortex + Live Prices (Premium)
                    <span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; margin: 0 5px;">📊 HYBRID</span> Live Prices + Enhanced Analysis
                    <span style="background: #6c757d; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; margin: 0 5px;">📝 DEMO</span> Professional Mock Data<br>
                    <div style="margin-top: 8px; font-size: 0.85rem; color: #a0a0b0;">
                        ⚡ <strong>Enhanced Features:</strong> Multi-factor scoring algorithm • Risk factor analysis • Price momentum integration • Professional breakdowns
                    </div>
                </div>`;
            
            results.forEach((result, index) => {
                const score = result.squeeze_score || 0;
                let scoreClass = 'score-low';
                if (score >= 80) scoreClass = 'score-extreme';
                else if (score >= 60) scoreClass = 'score-high';
                else if (score >= 40) scoreClass = 'score-medium';
                
                const ortex = result.ortex_data || {};
                const priceChangeColor = (result.price_change || 0) >= 0 ? '#00ff88' : '#ff6b6b';
                const priceChangeIcon = (result.price_change || 0) >= 0 ? '↗' : '↘';
                const volumeM = result.volume ? (result.volume / 1000000).toFixed(1) : 'N/A';
                
                // Data source indicator
                let dataSourceBadge = '';
                if (result.data_source === 'live_api') {
                    dataSourceBadge = '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; font-weight: bold;">🔴 LIVE</span>';
                } else if (result.data_source === 'mixed_live_price') {
                    dataSourceBadge = '<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; font-weight: bold;">📊 LIVE PRICE</span>';
                } else {
                    dataSourceBadge = '<span style="background: #6c757d; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; font-weight: bold;">📝 DEMO</span>';
                }
                
                html += `
                    <div class="result-item ${scoreClass}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <h4 style="margin: 0; color: #ff6b6b; font-size: 1.3rem;">#${index + 1} ${result.ticker}</h4>
                                ${dataSourceBadge}
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.4rem; font-weight: bold; color: #e0e0e0;">$${result.current_price || 'N/A'}</div>
                                <div style="color: ${priceChangeColor}; font-weight: bold;">
                                    ${priceChangeIcon} ${Math.abs(result.price_change || 0).toFixed(2)}%
                                </div>
                            </div>
                        </div>
                        <!-- Professional Score Breakdown -->
                        <div style="background: #1a1a2e; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <strong>🎯 Professional Score Breakdown:</strong>
                                <span style="font-size: 1.4rem; color: #ff6b6b; font-weight: bold;">${score}/100</span>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; font-size: 0.8rem;">
                                ${result.score_breakdown ? 
                                    `<div><strong>SI:</strong> ${result.score_breakdown.short_interest || 0}pts</div>
                                     <div><strong>Util:</strong> ${result.score_breakdown.utilization || 0}pts</div>
                                     <div><strong>CTB:</strong> ${result.score_breakdown.cost_to_borrow || 0}pts</div>
                                     <div><strong>DTC:</strong> ${result.score_breakdown.days_to_cover || 0}pts</div>` 
                                    : '<div colspan="4">Score breakdown not available</div>'}
                            </div>
                            <div style="margin-top: 8px; font-size: 0.8rem; color: #a0a0b0;">
                                <strong>⚠️ Risk Level:</strong> ${result.squeeze_type || 'Unknown'}
                                ${result.risk_factors && result.risk_factors.length > 0 ? 
                                    ` • <strong>Factors:</strong> ${result.risk_factors.slice(0,3).join(', ')}` : ''}
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; font-size: 0.9rem;">
                            <div>
                                <strong>📊 Short Interest:</strong><br>
                                <span style="font-size: 1.1rem; color: ${ortex.short_interest > 20 ? '#ff6b6b' : ortex.short_interest > 10 ? '#ffc107' : '#28a745'}; font-weight: bold;">${ortex.short_interest || 'N/A'}%</span><br><br>
                                <strong>📈 Utilization:</strong><br>
                                <span style="font-size: 1.1rem; color: ${ortex.utilization > 90 ? '#ff6b6b' : ortex.utilization > 75 ? '#ffc107' : '#28a745'}; font-weight: bold;">${ortex.utilization || 'N/A'}%</span><br><br>
                                <strong>💰 Cost to Borrow:</strong><br>
                                <span style="font-size: 1.1rem; color: ${ortex.cost_to_borrow > 15 ? '#ff6b6b' : ortex.cost_to_borrow > 5 ? '#ffc107' : '#28a745'}; font-weight: bold;">${ortex.cost_to_borrow || 'N/A'}%</span>
                            </div>
                            <div>
                                <strong>📅 Days to Cover:</strong><br>
                                <span style="font-size: 1.1rem; color: ${ortex.days_to_cover > 5 ? '#ff6b6b' : ortex.days_to_cover > 3 ? '#ffc107' : '#28a745'}; font-weight: bold;">${ortex.days_to_cover || 'N/A'}</span><br><br>
                                <strong>📊 Volume:</strong><br>
                                <span style="font-size: 1.1rem; font-weight: bold;">${volumeM}M</span><br><br>
                                <strong>📱 Data Source:</strong><br>
                                <span style="font-size: 0.8rem; color: #a0a0b0;">${result.price_source || result.data_source || 'Unknown'}</span>
                            </div>
                            <div>
                                <strong>🔥 Squeeze Indicators:</strong><br>
                                <div style="display: flex; flex-direction: column; gap: 3px;">
                                    ${ortex.short_interest > 20 ? 
                                        '<span style="color: #00ff88;">✅ High Short Interest</span>' : 
                                        '<span style="color: #ff6b6b;">❌ Low Short Interest</span>'}<br>
                                    ${ortex.utilization > 85 ? 
                                        '<span style="color: #00ff88;">✅ High Utilization</span>' : 
                                        '<span style="color: #ff6b6b;">❌ Low Utilization</span>'}<br>
                                    ${ortex.cost_to_borrow > 10 ? 
                                        '<span style="color: #00ff88;">✅ High Borrow Cost</span>' : 
                                        '<span style="color: #ff6b6b;">❌ Low Borrow Cost</span>'}<br>
                                    ${ortex.days_to_cover > 3 ? 
                                        '<span style="color: #00ff88;">✅ High Days to Cover</span>' : 
                                        '<span style="color: #ff6b6b;">❌ Low Days to Cover</span>'}
                                </div>
                            </div>
                        </div>
                    </div>`;
            });
            
            html += '</div>';
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_health(self):
        # Check if Ortex API key is available via environment variable
        has_ortex_env = bool(os.environ.get('ORTEX_API_KEY', ''))
        
        response = {
            'status': 'healthy',
            'message': 'Ultimate Squeeze Scanner API v6.0 with Live Ortex + Yahoo Finance Integration!',
            'timestamp': datetime.now().isoformat(),
            'version': '6.0.0-live-api',
            'ortex_env_configured': has_ortex_env
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_squeeze_scan(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode()) if post_data else {}
            
            # Get Ortex API key from form input or environment variable
            ortex_key = data.get('ortex_key', '') or os.environ.get('ORTEX_API_KEY', '')
            tickers = data.get('tickers', ['GME', 'AMC'])
            
            # Check if we should use live data
            use_live_data = ortex_key and len(ortex_key.strip()) >= 10
            
            # Comprehensive squeeze data with enhanced metrics
            mock_data = {
                # Meme Stock Legends
                'GME': {'score': 78, 'type': 'High Squeeze Risk', 'si': 22.5, 'dtc': 4.1, 'util': 89.2, 'ctb': 12.8, 'price': 18.75, 'change': 2.3, 'volume': 15420000},
                'AMC': {'score': 65, 'type': 'High Squeeze Risk', 'si': 18.7, 'dtc': 3.8, 'util': 82.1, 'ctb': 8.9, 'price': 4.82, 'change': -1.2, 'volume': 28750000},
                'BBBY': {'score': 85, 'type': 'EXTREME SQUEEZE RISK', 'si': 35.2, 'dtc': 6.2, 'util': 95.7, 'ctb': 28.4, 'price': 0.35, 'change': 8.7, 'volume': 45820000},
                
                # High Short Interest Plays
                'ATER': {'score': 72, 'type': 'High Squeeze Risk', 'si': 28.3, 'dtc': 4.7, 'util': 87.4, 'ctb': 18.2, 'price': 2.15, 'change': 3.4, 'volume': 8950000},
                'SPRT': {'score': 71, 'type': 'High Squeeze Risk', 'si': 28.1, 'dtc': 5.1, 'util': 88.9, 'ctb': 15.7, 'price': 1.85, 'change': -2.1, 'volume': 12340000},
                'IRNT': {'score': 58, 'type': 'Moderate Squeeze Risk', 'si': 19.8, 'dtc': 3.2, 'util': 79.3, 'ctb': 7.1, 'price': 12.40, 'change': 1.8, 'volume': 6780000},
                'OPAD': {'score': 63, 'type': 'High Squeeze Risk', 'si': 24.1, 'dtc': 4.0, 'util': 84.2, 'ctb': 11.5, 'price': 8.32, 'change': 4.2, 'volume': 3450000},
                'MRIN': {'score': 55, 'type': 'Moderate Squeeze Risk', 'si': 16.7, 'dtc': 2.8, 'util': 73.5, 'ctb': 6.8, 'price': 3.75, 'change': -0.8, 'volume': 2150000},
                'BGFV': {'score': 68, 'type': 'High Squeeze Risk', 'si': 25.4, 'dtc': 4.3, 'util': 86.1, 'ctb': 13.2, 'price': 15.67, 'change': 2.1, 'volume': 1890000},
                'PROG': {'score': 52, 'type': 'Moderate Squeeze Risk', 'si': 14.9, 'dtc': 2.5, 'util': 71.2, 'ctb': 5.4, 'price': 1.23, 'change': 1.7, 'volume': 7820000},
                
                # EV & Tech Squeeze Plays
                'NKLA': {'score': 61, 'type': 'High Squeeze Risk', 'si': 21.3, 'dtc': 3.9, 'util': 81.7, 'ctb': 9.8, 'price': 2.34, 'change': -3.2, 'volume': 9340000},
                'RIDE': {'score': 59, 'type': 'Moderate Squeeze Risk', 'si': 18.9, 'dtc': 3.4, 'util': 78.6, 'ctb': 8.1, 'price': 1.87, 'change': 1.9, 'volume': 4560000},
                'WKHS': {'score': 57, 'type': 'Moderate Squeeze Risk', 'si': 17.2, 'dtc': 3.1, 'util': 75.8, 'ctb': 7.3, 'price': 3.42, 'change': 0.6, 'volume': 3280000},
                'GOEV': {'score': 48, 'type': 'Low Squeeze Risk', 'si': 13.8, 'dtc': 2.2, 'util': 68.4, 'ctb': 4.7, 'price': 0.89, 'change': -1.1, 'volume': 2750000},
                
                # Biotech & Healthcare
                'SAVA': {'score': 74, 'type': 'High Squeeze Risk', 'si': 29.7, 'dtc': 5.3, 'util': 89.8, 'ctb': 19.4, 'price': 8.45, 'change': 3.8, 'volume': 5670000},
                'VXRT': {'score': 66, 'type': 'High Squeeze Risk', 'si': 23.6, 'dtc': 4.2, 'util': 83.9, 'ctb': 12.1, 'price': 2.78, 'change': 2.4, 'volume': 4320000},
                'CLOV': {'score': 54, 'type': 'Moderate Squeeze Risk', 'si': 15.8, 'dtc': 2.7, 'util': 72.6, 'ctb': 6.2, 'price': 1.95, 'change': 1.3, 'volume': 8950000},
                'BYND': {'score': 62, 'type': 'High Squeeze Risk', 'si': 22.4, 'dtc': 4.1, 'util': 82.7, 'ctb': 10.6, 'price': 7.89, 'change': -2.7, 'volume': 3180000},
                
                # Retail & Consumer
                'APRN': {'score': 69, 'type': 'High Squeeze Risk', 'si': 26.8, 'dtc': 4.6, 'util': 87.3, 'ctb': 14.9, 'price': 12.34, 'change': 4.7, 'volume': 2890000},
                'UPST': {'score': 64, 'type': 'High Squeeze Risk', 'si': 24.7, 'dtc': 4.4, 'util': 85.1, 'ctb': 12.8, 'price': 28.56, 'change': 1.9, 'volume': 4560000},
                'SKLZ': {'score': 51, 'type': 'Moderate Squeeze Risk', 'si': 14.2, 'dtc': 2.4, 'util': 69.7, 'ctb': 5.1, 'price': 1.45, 'change': -0.7, 'volume': 6780000},
                'WISH': {'score': 49, 'type': 'Low Squeeze Risk', 'si': 13.1, 'dtc': 2.1, 'util': 66.8, 'ctb': 4.3, 'price': 0.67, 'change': 2.1, 'volume': 12450000},
                
                # Energy & Resources
                'GEVO': {'score': 58, 'type': 'Moderate Squeeze Risk', 'si': 18.4, 'dtc': 3.3, 'util': 77.2, 'ctb': 7.9, 'price': 1.89, 'change': 1.6, 'volume': 5230000},
                'KOSS': {'score': 67, 'type': 'High Squeeze Risk', 'si': 25.1, 'dtc': 4.5, 'util': 86.4, 'ctb': 13.7, 'price': 4.23, 'change': 5.8, 'volume': 2840000},
                'NAKD': {'score': 45, 'type': 'Low Squeeze Risk', 'si': 11.9, 'dtc': 1.8, 'util': 63.2, 'ctb': 3.7, 'price': 0.34, 'change': -1.4, 'volume': 18900000},
                'EXPR': {'score': 53, 'type': 'Moderate Squeeze Risk', 'si': 15.6, 'dtc': 2.6, 'util': 71.9, 'ctb': 5.8, 'price': 1.76, 'change': 0.9, 'volume': 4670000},
                
                # SPACs & New Plays
                'DWAC': {'score': 76, 'type': 'High Squeeze Risk', 'si': 31.2, 'dtc': 5.7, 'util': 91.4, 'ctb': 21.3, 'price': 16.89, 'change': 6.2, 'volume': 15670000},
                'PHUN': {'score': 70, 'type': 'High Squeeze Risk', 'si': 27.8, 'dtc': 4.9, 'util': 88.6, 'ctb': 16.4, 'price': 0.89, 'change': 12.7, 'volume': 35670000},
                'BKKT': {'score': 56, 'type': 'Moderate Squeeze Risk', 'si': 17.5, 'dtc': 3.0, 'util': 74.8, 'ctb': 6.9, 'price': 2.45, 'change': 2.8, 'volume': 6780000},
                'MARK': {'score': 60, 'type': 'High Squeeze Risk', 'si': 20.3, 'dtc': 3.7, 'util': 80.1, 'ctb': 9.2, 'price': 1.67, 'change': 3.4, 'volume': 8920000},
                
                # Penny Squeeze Plays
                'SNDL': {'score': 47, 'type': 'Low Squeeze Risk', 'si': 12.7, 'dtc': 1.9, 'util': 65.3, 'ctb': 4.1, 'price': 0.78, 'change': 1.2, 'volume': 45670000},
                'CCIV': {'score': 54, 'type': 'Moderate Squeeze Risk', 'si': 16.1, 'dtc': 2.8, 'util': 73.1, 'ctb': 6.4, 'price': 3.89, 'change': -1.8, 'volume': 7890000},
                'PSTH': {'score': 42, 'type': 'Low Squeeze Risk', 'si': 10.8, 'dtc': 1.6, 'util': 59.7, 'ctb': 3.2, 'price': 19.23, 'change': 0.4, 'volume': 2340000},
                
                # Popular Recent Squeeze Plays
                'RDBX': {'score': 73, 'type': 'High Squeeze Risk', 'si': 29.8, 'dtc': 5.2, 'util': 88.4, 'ctb': 17.3, 'price': 2.45, 'change': 5.6, 'volume': 18750000},
                'MULN': {'score': 56, 'type': 'Moderate Squeeze Risk', 'si': 17.4, 'dtc': 3.1, 'util': 76.2, 'ctb': 8.7, 'price': 0.89, 'change': 3.2, 'volume': 12450000},
                'ENDP': {'score': 69, 'type': 'High Squeeze Risk', 'si': 26.7, 'dtc': 4.8, 'util': 85.9, 'ctb': 14.2, 'price': 1.56, 'change': -2.4, 'volume': 8970000},
                'CANO': {'score': 61, 'type': 'High Squeeze Risk', 'si': 22.1, 'dtc': 4.0, 'util': 82.3, 'ctb': 11.8, 'price': 3.78, 'change': 1.8, 'volume': 6540000},
                'GNUS': {'score': 48, 'type': 'Low Squeeze Risk', 'si': 13.9, 'dtc': 2.3, 'util': 68.7, 'ctb': 5.9, 'price': 0.67, 'change': 4.1, 'volume': 9870000},
                
                # Extended Meme/Reddit Favorites
                'NOK': {'score': 52, 'type': 'Moderate Squeeze Risk', 'si': 15.2, 'dtc': 2.7, 'util': 71.8, 'ctb': 6.3, 'price': 4.23, 'change': 0.9, 'volume': 34560000},
                'BB': {'score': 58, 'type': 'Moderate Squeeze Risk', 'si': 18.6, 'dtc': 3.5, 'util': 78.1, 'ctb': 8.4, 'price': 5.67, 'change': -1.3, 'volume': 12780000},
                'PLTR': {'score': 64, 'type': 'High Squeeze Risk', 'si': 23.4, 'dtc': 4.2, 'util': 84.6, 'ctb': 12.1, 'price': 8.92, 'change': 2.7, 'volume': 18940000},
                'TLRY': {'score': 59, 'type': 'Moderate Squeeze Risk', 'si': 19.7, 'dtc': 3.6, 'util': 79.5, 'ctb': 9.1, 'price': 2.89, 'change': 1.4, 'volume': 8760000},
                'RKT': {'score': 55, 'type': 'Moderate Squeeze Risk', 'si': 16.8, 'dtc': 3.0, 'util': 74.2, 'ctb': 7.5, 'price': 6.45, 'change': -0.8, 'volume': 5430000},
                
                # Biotech & Health Expanded
                'NVAX': {'score': 66, 'type': 'High Squeeze Risk', 'si': 24.9, 'dtc': 4.5, 'util': 86.7, 'ctb': 13.8, 'price': 12.34, 'change': 3.9, 'volume': 7890000},
                'OCGN': {'score': 63, 'type': 'High Squeeze Risk', 'si': 22.8, 'dtc': 4.1, 'util': 83.4, 'ctb': 11.6, 'price': 1.78, 'change': 2.1, 'volume': 9650000},
                'SRNE': {'score': 57, 'type': 'Moderate Squeeze Risk', 'si': 17.9, 'dtc': 3.3, 'util': 77.6, 'ctb': 8.9, 'price': 0.89, 'change': -1.7, 'volume': 6780000},
                'SESN': {'score': 51, 'type': 'Moderate Squeeze Risk', 'si': 14.6, 'dtc': 2.6, 'util': 70.3, 'ctb': 6.7, 'price': 0.34, 'change': 1.9, 'volume': 4560000},
                
                # EV & Tech Expanded  
                'ARVL': {'score': 60, 'type': 'High Squeeze Risk', 'si': 21.5, 'dtc': 3.8, 'util': 81.2, 'ctb': 10.4, 'price': 1.23, 'change': 2.8, 'volume': 7890000},
                'LCID': {'score': 62, 'type': 'High Squeeze Risk', 'si': 22.7, 'dtc': 4.0, 'util': 82.9, 'ctb': 11.3, 'price': 3.45, 'change': -2.1, 'volume': 15670000},
                'RIVN': {'score': 58, 'type': 'Moderate Squeeze Risk', 'si': 18.3, 'dtc': 3.4, 'util': 78.7, 'ctb': 8.6, 'price': 12.89, 'change': 1.6, 'volume': 12340000},
                'XPEV': {'score': 56, 'type': 'Moderate Squeeze Risk', 'si': 17.1, 'dtc': 3.1, 'util': 75.4, 'ctb': 7.8, 'price': 8.67, 'change': 0.7, 'volume': 8970000},
                'NIO': {'score': 59, 'type': 'Moderate Squeeze Risk', 'si': 19.4, 'dtc': 3.5, 'util': 79.1, 'ctb': 9.3, 'price': 5.23, 'change': -0.9, 'volume': 23450000},
                
                # Crypto Related
                'COIN': {'score': 67, 'type': 'High Squeeze Risk', 'si': 25.6, 'dtc': 4.6, 'util': 87.3, 'ctb': 14.7, 'price': 89.45, 'change': 4.2, 'volume': 8760000},
                'RIOT': {'score': 64, 'type': 'High Squeeze Risk', 'si': 23.8, 'dtc': 4.3, 'util': 84.1, 'ctb': 12.9, 'price': 7.89, 'change': 3.5, 'volume': 12890000},
                'MARA': {'score': 61, 'type': 'High Squeeze Risk', 'si': 21.9, 'dtc': 3.9, 'util': 82.6, 'ctb': 11.1, 'price': 14.56, 'change': 2.8, 'volume': 9870000},
                'HUT': {'score': 53, 'type': 'Moderate Squeeze Risk', 'si': 15.7, 'dtc': 2.9, 'util': 72.8, 'ctb': 6.9, 'price': 2.34, 'change': 1.4, 'volume': 6540000},
                'BITF': {'score': 55, 'type': 'Moderate Squeeze Risk', 'si': 16.4, 'dtc': 3.0, 'util': 74.5, 'ctb': 7.2, 'price': 1.89, 'change': 0.8, 'volume': 5430000},
                'SI': {'score': 49, 'type': 'Low Squeeze Risk', 'si': 13.2, 'dtc': 2.4, 'util': 67.9, 'ctb': 5.6, 'price': 12.67, 'change': -1.2, 'volume': 3210000},
                
                # AI & Machine Learning
                'NVDA': {'score': 45, 'type': 'Low Squeeze Risk', 'si': 11.8, 'dtc': 2.1, 'util': 64.2, 'ctb': 4.3, 'price': 456.78, 'change': 2.1, 'volume': 34560000},
                'AMD': {'score': 48, 'type': 'Low Squeeze Risk', 'si': 12.9, 'dtc': 2.3, 'util': 67.1, 'ctb': 5.1, 'price': 98.45, 'change': 1.7, 'volume': 28790000},
                'C3AI': {'score': 59, 'type': 'Moderate Squeeze Risk', 'si': 19.2, 'dtc': 3.6, 'util': 78.9, 'ctb': 9.0, 'price': 16.89, 'change': 3.4, 'volume': 6780000},
                'AI': {'score': 62, 'type': 'High Squeeze Risk', 'si': 22.4, 'dtc': 4.0, 'util': 83.7, 'ctb': 11.9, 'price': 23.45, 'change': 2.9, 'volume': 8970000},
                'SNOW': {'score': 54, 'type': 'Moderate Squeeze Risk', 'si': 16.3, 'dtc': 2.9, 'util': 73.6, 'ctb': 7.1, 'price': 145.67, 'change': 1.2, 'volume': 4560000},
                'NET': {'score': 51, 'type': 'Moderate Squeeze Risk', 'si': 14.7, 'dtc': 2.6, 'util': 70.8, 'ctb': 6.4, 'price': 67.89, 'change': 0.9, 'volume': 3210000},
                'DDOG': {'score': 50, 'type': 'Moderate Squeeze Risk', 'si': 14.1, 'dtc': 2.5, 'util': 69.4, 'ctb': 6.0, 'price': 89.23, 'change': -0.6, 'volume': 2890000},
                
                # Large Cap Institutional Targets
                'TSLA': {'score': 58, 'type': 'Moderate Squeeze Risk', 'si': 18.5, 'dtc': 3.4, 'util': 78.3, 'ctb': 8.7, 'price': 234.56, 'change': 3.2, 'volume': 45670000},
                'AAPL': {'score': 32, 'type': 'Low Squeeze Risk', 'si': 8.4, 'dtc': 1.5, 'util': 52.1, 'ctb': 2.8, 'price': 178.90, 'change': 0.8, 'volume': 67890000},
                'NFLX': {'score': 46, 'type': 'Low Squeeze Risk', 'si': 12.3, 'dtc': 2.2, 'util': 66.7, 'ctb': 4.9, 'price': 423.45, 'change': -1.4, 'volume': 8970000},
                'SHOP': {'score': 56, 'type': 'Moderate Squeeze Risk', 'si': 17.6, 'dtc': 3.2, 'util': 76.8, 'ctb': 8.1, 'price': 45.67, 'change': 2.3, 'volume': 6780000},
                'ROKU': {'score': 61, 'type': 'High Squeeze Risk', 'si': 21.7, 'dtc': 3.9, 'util': 82.4, 'ctb': 10.9, 'price': 56.78, 'change': 4.1, 'volume': 9870000},
                'PTON': {'score': 65, 'type': 'High Squeeze Risk', 'si': 24.3, 'dtc': 4.4, 'util': 85.6, 'ctb': 13.2, 'price': 8.90, 'change': 5.7, 'volume': 12340000},
                'ZM': {'score': 52, 'type': 'Moderate Squeeze Risk', 'si': 15.4, 'dtc': 2.8, 'util': 72.3, 'ctb': 6.8, 'price': 67.45, 'change': -0.9, 'volume': 5430000},
                'HOOD': {'score': 63, 'type': 'High Squeeze Risk', 'si': 23.1, 'dtc': 4.1, 'util': 84.0, 'ctb': 12.3, 'price': 9.87, 'change': 3.6, 'volume': 15670000}
            }
            
            results = []
            live_data_count = 0
            
            for ticker in tickers:
                ticker = ticker.upper()
                
                # Try to get live data first
                ortex_data = None
                price_data = None
                
                if use_live_data:
                    ortex_data = self.get_ortex_data(ticker, ortex_key)
                    price_data = self.get_stock_price_data(ticker)
                    
                    if ortex_data or price_data:
                        live_data_count += 1
                
                # Use live data if available, otherwise fall back to mock data
                if ortex_data and price_data:
                    # Calculate squeeze score from live data with detailed breakdown
                    squeeze_score, score_details = self.calculate_squeeze_score(ortex_data, price_data)
                    squeeze_type = self.get_squeeze_type(squeeze_score)
                    
                    results.append({
                        'ticker': ticker,
                        'squeeze_score': squeeze_score,
                        'squeeze_type': squeeze_type,
                        'current_price': price_data['current_price'],
                        'price_change': price_data['price_change'],
                        'volume': price_data['volume'],
                        'ortex_data': ortex_data,
                        'score_breakdown': score_details['breakdown'],
                        'risk_factors': score_details['risk_factors'],
                        'data_source': 'live_api',
                        'price_source': price_data.get('source', 'unknown'),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                elif price_data and ticker in mock_data:
                    # Mix live price data with mock Ortex data
                    mock = mock_data[ticker]
                    mock_ortex = {
                        'short_interest': mock['si'],
                        'days_to_cover': mock['dtc'],
                        'utilization': mock['util'],
                        'cost_to_borrow': mock['ctb']
                    }
                    
                    # Calculate score with enhanced algorithm
                    squeeze_score, score_details = self.calculate_squeeze_score(mock_ortex, price_data)
                    squeeze_type = self.get_squeeze_type(squeeze_score)
                    
                    results.append({
                        'ticker': ticker,
                        'squeeze_score': squeeze_score,
                        'squeeze_type': squeeze_type,
                        'current_price': price_data['current_price'],
                        'price_change': price_data['price_change'],
                        'volume': price_data['volume'],
                        'ortex_data': mock_ortex,
                        'score_breakdown': score_details['breakdown'],
                        'risk_factors': score_details['risk_factors'],
                        'data_source': 'mixed_live_price',
                        'price_source': price_data.get('source', 'unknown'),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                elif ticker in mock_data:
                    # Use pure mock data as fallback
                    mock = mock_data[ticker]
                    mock_ortex = {
                        'short_interest': mock['si'],
                        'days_to_cover': mock['dtc'],
                        'utilization': mock['util'],
                        'cost_to_borrow': mock['ctb']
                    }
                    mock_price = {
                        'current_price': mock['price'],
                        'price_change': mock['change'],
                        'volume': mock['volume'],
                        'source': 'mock_data'
                    }
                    
                    # Calculate score with enhanced algorithm
                    squeeze_score, score_details = self.calculate_squeeze_score(mock_ortex, mock_price)
                    squeeze_type = self.get_squeeze_type(squeeze_score)
                    
                    results.append({
                        'ticker': ticker,
                        'squeeze_score': squeeze_score,
                        'squeeze_type': squeeze_type,
                        'current_price': mock['price'],
                        'price_change': mock['change'],
                        'volume': mock['volume'],
                        'ortex_data': mock_ortex,
                        'score_breakdown': score_details['breakdown'],
                        'risk_factors': score_details['risk_factors'],
                        'data_source': 'mock_data',
                        'price_source': 'mock_data',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Sort by squeeze score descending
            results.sort(key=lambda x: x['squeeze_score'], reverse=True)
            
            # Generate appropriate message
            if use_live_data and live_data_count > 0:
                data_message = f"Using live data for {live_data_count} tickers, mock data for others"
            elif use_live_data:
                data_message = "Ortex API key provided but no live data retrieved - using enhanced mock data"
            else:
                data_message = "Using enhanced mock data (provide Ortex API key for live data)"
            
            response = {
                'success': True,
                'results': results,
                'count': len(results),
                'live_data_count': live_data_count,
                'message': f'Found {len(results)} squeeze candidates - {data_message}'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'message': 'Error during squeeze scan'
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def send_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error = {'error': 'Not Found'}
        self.wfile.write(json.dumps(error).encode())