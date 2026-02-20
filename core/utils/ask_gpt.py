import json
import re
import json_repair
from openai import OpenAI
from core.utils.config_utils import load_key
from core.utils.decorator import except_handler

# Try to import anthropic, but don't fail if not available
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# ------------
# ask gpt once
# ------------

@except_handler("GPT request failed", retry=5)
def ask_gpt(prompt, resp_type=None, valid_def=None, log_title="default"):
    if not load_key("api.key"):
        raise ValueError("API key is not set")

    model = load_key("api.model")
    api_key = load_key("api.key")
    base_url = load_key("api.base_url")
    api_format = load_key("api.format") or "openai"

    if api_format == "anthropic":
        # Anthropic format
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package is not installed. Please install it with: pip install anthropic")

        # Handle base URL for Anthropic (optional, for compatible proxies)
        client_kwargs = {"api_key": api_key}
        if base_url and base_url not in ["https://api.anthropic.com", ""]:
            client_kwargs["base_url"] = base_url

        client = anthropic.Anthropic(**client_kwargs)

        # Prepare system message if JSON mode is requested
        system_msg = ""
        if resp_type == "json" and load_key("api.llm_support_json"):
            system_msg = "Please respond in JSON format."

        params = dict(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            timeout=300
        )
        if system_msg:
            params["system"] = system_msg

        resp_raw = client.messages.create(**params)
        resp_content = resp_raw.content[0].text if resp_raw.content else ""

    else:
        # OpenAI format (default)
        if 'ark' in base_url:
            base_url = "https://ark.cn-beijing.volces.com/api/v3" # huoshan base url
        elif 'v1' not in base_url:
            base_url = base_url.strip('/') + '/v1'
        client = OpenAI(api_key=api_key, base_url=base_url)

        # Always use response_format for JSON mode when supported
        response_format = None
        if resp_type == "json" and load_key("api.llm_support_json"):
            response_format = {"type": "json_object"}

        messages = [{"role": "user", "content": prompt}]

        params = dict(
            model=model,
            messages=messages,
            timeout=300
        )
        if response_format:
            params["response_format"] = response_format

        # Use extra_body for MiniMax reasoning_split parameter
        if resp_type == "json":
            params["extra_body"] = {"reasoning_split": True}

        resp_raw = client.chat.completions.create(**params)

        # process and return full result
        # When reasoning_split=True, JSON is in content, thinking is in reasoning_details
        msg = resp_raw.choices[0].message
        resp_content = msg.content

    if resp_type == "json":
        try:
            resp = json_repair.loads(resp_content)
        except Exception as e:
            raise ValueError(f"❎ JSON parse error: {e}")

        # Basic validation: ensure it's a dict, not a list or other type
        if not isinstance(resp, dict):
            raise ValueError(f"❎ Expected JSON object, got {type(resp).__name__}: {str(resp)[:200]}")

    else:
        resp = resp_content

    # check if the response format is valid
    # Always validate when JSON mode is enabled
    if valid_def and load_key("api.llm_support_json"):
        valid_resp = valid_def(resp)
        if valid_resp['status'] != 'success':
            raise ValueError(f"❎ API response error: {valid_resp['message']}")

    return resp


if __name__ == '__main__':
    from rich import print as rprint

    result = ask_gpt("""test respond ```json\n{\"code\": 200, \"message\": \"success\"}\n```""", resp_type="json")
    rprint(f"Test json output result: {result}")
