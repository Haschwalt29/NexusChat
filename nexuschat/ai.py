import json
import logging
import time
import requests
from .database import db
from .config import config

logger = logging.getLogger(__name__)

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"


def _post_openai(payload: dict) -> requests.Response:
	"""Post to OpenAI with a short timeout."""
	headers = {
		"Authorization": f"Bearer {config.OPENAI_API_KEY}",
		"Content-Type": "application/json",
	}
	return requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(payload), timeout=20)


def _friendly_error_from_openai(resp: requests.Response) -> str:
	"""Map OpenAI error responses to friendly messages."""
	try:
		data = resp.json()
		err = (data or {}).get("error", {})
		code = err.get("code") or err.get("type")
		message = err.get("message", "")
	except Exception:
		data, code, message = None, None, ""
	
	status = resp.status_code
	logger.error(f"OpenAI API error {status}: {resp.text[:400]}")
	
	if status == 401:
		return "AI configuration error: invalid API key."
	if status == 404:
		return "Requested AI model is not available. Please set OPENAI_MODEL to a valid model."
	if status == 429:
		if code == "insufficient_quota" or "quota" in message.lower():
			return "quota_exceeded"
		return "rate_limited"
	return "other_error"


def _call_gemini(conversation: list) -> str:
	"""Call Gemini API with conversation messages and return text or error string."""
	if not config.GEMINI_API_KEY:
		return "Gemini API key missing."
	
	# Convert OpenAI-style messages to Gemini's contents format
	contents = []
	for msg in conversation:
		role = msg.get("role")
		text = msg.get("content", "")
		if not text:
			continue
		parts = [{"text": text}]
		if role == "user":
			contents.append({"role": "user", "parts": parts})
		else:
			contents.append({"role": "model", "parts": parts})
	
	payload = {
		"contents": contents,
		"generationConfig": {
			"temperature": 0.7,
			"maxOutputTokens": 150
		}
	}
	url = GEMINI_API_URL.format(model=config.GEMINI_MODEL, api_key=config.GEMINI_API_KEY)
	resp = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=20)
	if resp.status_code != 200:
		logger.error(f"Gemini API error {resp.status_code}: {resp.text[:400]}")
		return "Gemini service error."
	data = resp.json()
	try:
		candidates = data.get("candidates") or []
		text = candidates[0]["content"]["parts"][0]["text"].strip()
		return text or "I couldn't generate a response. Please try again."
	except Exception:
		return "I couldn't generate a response. Please try again."


def generate_ai_reply(username: str) -> str:
	"""
	Generate AI reply using OpenAI first; if quota/rate limited and Gemini is configured, fall back to Gemini.
	"""
	try:
		# Build conversation from recent messages
		messages = list(
			db.messages.find({"username": username}).sort("created_at", -1).limit(10)
		)
		messages.reverse()
		conversation = [
			{
				"role": "system",
				"content": (
					"You are a helpful AI assistant in a chat application. "
					"Keep responses concise, friendly, and engaging."
				),
			}
		]
		for msg in messages:
			role = "assistant" if msg.get("sender") == "ai" else "user"
			conversation.append({
				"role": role,
				"content": msg.get("content", "") or "",
			})
		
		# Try OpenAI first if configured
		if config.OPENAI_API_KEY:
			payload = {
				"model": config.OPENAI_MODEL,
				"messages": conversation,
				"max_tokens": 150,
				"temperature": 0.7,
			}
			resp = _post_openai(payload)
			if resp.status_code == 429:
				time.sleep(1.5)
				resp = _post_openai(payload)
			if resp.status_code == 200:
				data = resp.json()
				return (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip() or "I couldn't generate a response. Please try again."
			else:
				category = _friendly_error_from_openai(resp)
				if category in ("quota_exceeded", "rate_limited") and config.GEMINI_API_KEY:
					# Fallback to Gemini
					return _call_gemini(conversation)
				# Otherwise return user-friendly string
				if category == "other_error":
					return "AI service error. Please try again."
				return "AI configuration error or model issue."
		
		# If OpenAI not configured, try Gemini directly
		if config.GEMINI_API_KEY:
			return _call_gemini(conversation)
		
		return "AI service is not configured. Please set API keys."
	
	except requests.Timeout:
		return "AI service timed out. Please try again."
	except Exception as e:
		logger.exception(f"Unexpected error in AI generation: {e}")
		return "An unexpected error occurred while generating a reply."



