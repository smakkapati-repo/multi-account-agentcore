import json
import boto3
import os

bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        prompt = body.get('prompt', '')
        
        agent_runtime_arn = os.environ['AGENT_ARN']
        
        payload = {
            'prompt': prompt
        }
        
        print(f"Invoking agent: {agent_runtime_arn}")
        print(f"Payload: {payload}")
        
        response = bedrock_agentcore.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            payload=json.dumps(payload),
            contentType='application/json',
            accept='application/json'
        )
        
        print(f"Response keys: {response.keys()}")
        
        # Parse SSE streaming response and extract final text
        result = ''
        current_text = ''
        if 'response' in response:
            print("Reading response stream...")
            response_stream = response['response']
            byte_buffer = b''
            line_buffer = ''
            
            for chunk_bytes in response_stream:
                if isinstance(chunk_bytes, str):
                    chunk_bytes = chunk_bytes.encode('utf-8')
                byte_buffer += chunk_bytes
                
                # Try to decode buffer
                try:
                    chunk_str = byte_buffer.decode('utf-8')
                    byte_buffer = b''
                except UnicodeDecodeError:
                    continue
                
                # Add to line buffer and process complete lines
                line_buffer += chunk_str
                lines = line_buffer.split('\n')
                line_buffer = lines[-1]  # Keep incomplete line
                
                for line in lines[:-1]:
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            if 'event' in data and 'contentBlockDelta' in data['event']:
                                delta = data['event']['contentBlockDelta'].get('delta', {})
                                if 'text' in delta:
                                    current_text += delta['text']
                            elif 'event' in data and 'messageStop' in data['event']:
                                result = current_text
                        except:
                            pass
        
        # If no messageStop, use accumulated text
        if not result:
            result = current_text
        
        print(f"Final result length: {len(result)}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'response': result})
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error: {error_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e), 'trace': error_trace})
        }
