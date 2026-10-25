"""Create Twilio Functions for StarPulse call webhooks.

All secrets are read from environment variables.
Set them before running:
  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
  TWILIO_SERVICE_SID, TWILIO_ENV_SID,
  DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_WAREHOUSE,
  ANTHROPIC_API_KEY
"""
import os
import requests
import json
import time

ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
SERVICE_SID = os.environ.get("TWILIO_SERVICE_SID", "ZS06daee267ecf63af12c75ffec7f89302")
ENV_SID = os.environ.get("TWILIO_ENV_SID", "ZE19d6f0994888107842504c01ade7d114")

auth = (ACCOUNT_SID, AUTH_TOKEN)
base_api = f"https://serverless-upload.twilio.com/v1/Services/{SERVICE_SID}"

# ── Shared: Databricks logging helper (injected into each function) ──
DB_LOG_HELPER = """
const https = require('https');

function logToDb(context, callSid, status, detail, memberSelection) {
  const host = (context.DATABRICKS_HOST || '').replace('https://','').replace('/','');
  const token = context.DATABRICKS_TOKEN || '';
  const warehouse = context.DATABRICKS_WAREHOUSE || '';
  if (!host || !token || !warehouse) { console.log('DB logging skipped: missing env vars'); return; }

  const now = new Date().toISOString().replace('T',' ').substring(0,19);
  const ts = now.substring(11,19);
  const esc = (s) => (s||'').replace(/'/g,"''");
  const entry = '[' + ts + '] ' + esc(status) + (detail ? ': ' + esc(detail) : '');

  let setClauses = "status = '" + esc(status) + "', " +
    "interaction_log = CASE WHEN interaction_log IS NULL OR interaction_log = '' THEN '" + entry + "' ELSE interaction_log || ' | ' || '" + entry + "' END, " +
    "updated_at = '" + now + "'";
  if (memberSelection) {
    setClauses += ", member_selection = '" + esc(memberSelection) + "'";
  }

  const sql = "UPDATE aiagenticdemo.stars_silver.outreach_activity_log SET " + setClauses + " WHERE provider_sid = '" + esc(callSid) + "'";
  const body = JSON.stringify({ warehouse_id: warehouse, statement: sql, wait_timeout: '10s' });

  const req = https.request({
    hostname: host, path: '/api/2.0/sql/statements', method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
  }, (res) => {
    let data = '';
    res.on('data', (c) => data += c);
    res.on('end', () => console.log('DB log:', res.statusCode, data.substring(0,200)));
  });
  req.on('error', (e) => console.error('DB log error:', e.message));
  req.write(body);
  req.end();
}
"""

# ── Function 1: call-gather ──────────────────────────────────────
GATHER_CODE = DB_LOG_HELPER + """
exports.handler = function(context, event, callback) {
  const twiml = new Twilio.twiml.VoiceResponse();
  const digits = event.Digits || '';
  const callSid = event.CallSid || '';
  const baseUrl = 'https://' + context.DOMAIN_NAME;

  if (digits === '1') {
    logToDb(context, callSid, 'scheduling', 'Member pressed 1 - scheduling appointment');
    const gather = twiml.gather({
      numDigits: 1,
      action: baseUrl + '/call-slot',
      method: 'POST',
      timeout: 10,
    });
    gather.say({ voice: 'Polly.Joanna-Neural' },
      'Great! Here are available time slots.'
    );
    gather.pause({ length: 1 });
    gather.say({ voice: 'Polly.Joanna-Neural' },
      'Press 1 for tomorrow morning at 9 A M.'
    );
    gather.pause({ length: 1 });
    gather.say({ voice: 'Polly.Joanna-Neural' },
      'Press 2 for tomorrow afternoon at 2 P M.'
    );
    gather.pause({ length: 1 });
    gather.say({ voice: 'Polly.Joanna-Neural' },
      'Press 3 for tomorrow afternoon at 3 30 P M.'
    );
    gather.pause({ length: 1 });
    gather.say({ voice: 'Polly.Joanna-Neural' },
      'Press 4 to request a callback with more options.'
    );
    twiml.say({ voice: 'Polly.Joanna-Neural' },
      'We did not receive your selection. A coordinator will call you to schedule. Goodbye.'
    );
  } else if (digits === '2') {
    logToDb(context, callSid, 'ai-conversation', 'Member pressed 2 - AI care coordinator');
    const gather = twiml.gather({
      input: 'speech',
      action: baseUrl + '/call-agent',
      method: 'POST',
      speechTimeout: '2',
      timeout: 10,
      language: 'en-US',
    });
    gather.pause({ length: 1 });
    gather.say({ voice: 'Polly.Joanna-Neural' },
      'Hi, I am your StarPulse care coordinator. How can I help you today?'
    );
    twiml.say({ voice: 'Polly.Joanna-Neural' },
      'I did not hear anything. Thank you for your time. Goodbye.'
    );
  } else {
    logToDb(context, callSid, 'no-action', 'No valid selection', 'No time slot selected');
    twiml.say({ voice: 'Polly.Joanna-Neural' },
      'Thank you for your time. Goodbye.'
    );
  }
  callback(null, twiml);
};
"""

# ── Function 2: call-slot ────────────────────────────────────────
SLOT_CODE = DB_LOG_HELPER + """
exports.handler = function(context, event, callback) {
  const twiml = new Twilio.twiml.VoiceResponse();
  const digits = event.Digits || '';
  const callSid = event.CallSid || '';
  const slots = {
    '1': 'tomorrow morning at 9 AM',
    '2': 'tomorrow afternoon at 2 PM',
    '3': 'tomorrow afternoon at 3:30 PM',
    '4': 'callback requested',
  };
  const slot = slots[digits] || 'No time slot selected';

  if (digits === '4') {
    logToDb(context, callSid, 'scheduled', 'Callback requested', 'Scheduled: callback requested');
    twiml.say({ voice: 'Polly.Joanna-Neural' },
      'Your callback request has been noted. A care coordinator will reach out within 24 hours. Thank you and have a great day!'
    );
  } else if (slots[digits]) {
    logToDb(context, callSid, 'scheduled', 'Slot selected: ' + slot, 'Scheduled: ' + slot);
    twiml.say({ voice: 'Polly.Joanna-Neural' },
      'You are confirmed for ' + slot + '. You will receive an SMS confirmation shortly. Thank you and have a great day!'
    );
  } else {
    logToDb(context, callSid, 'no-action', 'No time slot selected', 'No time slot selected');
    twiml.say({ voice: 'Polly.Joanna-Neural' },
      'We did not receive a valid selection. A coordinator will call you to schedule. Goodbye.'
    );
  }
  callback(null, twiml);
};
"""

# ── Function 3: call-agent (Claude AI) ───────────────────────────
AGENT_CODE = DB_LOG_HELPER + """
const conversations = {};

exports.handler = async function(context, event, callback) {
  const twiml = new Twilio.twiml.VoiceResponse();
  const callSid = event.CallSid || '';
  const speech = event.SpeechResult || '';
  const baseUrl = 'https://' + context.DOMAIN_NAME;

  if (!speech) {
    const gather = twiml.gather({
      input: 'speech', action: baseUrl + '/call-agent', method: 'POST',
      speechTimeout: '2', timeout: 10, language: 'en-US',
    });
    gather.pause({ length: 1 });
    gather.say({ voice: 'Polly.Joanna-Neural' }, 'I did not catch that. Could you please repeat?');
    twiml.say({ voice: 'Polly.Joanna-Neural' }, 'Thank you for your time. Goodbye.');
    return callback(null, twiml);
  }

  if (!conversations[callSid]) conversations[callSid] = [];
  conversations[callSid].push({ role: 'user', content: speech });

  // Log each member speech turn
  logToDb(context, callSid, 'ai-conversation', 'Member: ' + speech.substring(0, 100));

  try {
    const aiReply = await callClaude(context.ANTHROPIC_API_KEY, conversations[callSid]);
    conversations[callSid].push({ role: 'assistant', content: aiReply });

    // Log AI response
    logToDb(context, callSid, 'ai-conversation', 'AI: ' + aiReply.substring(0, 100));

    const keys = Object.keys(conversations);
    if (keys.length > 30) delete conversations[keys[0]];

    const goodbyeWords = ['goodbye', 'bye', 'take care', 'have a great day'];
    const isEnding = goodbyeWords.some(w => aiReply.toLowerCase().includes(w));

    if (isEnding) {
      twiml.pause({ length: 1 });
      twiml.say({ voice: 'Polly.Joanna-Neural' }, aiReply);
      logToDb(context, callSid, 'ai-completed', 'AI conversation ended', 'AI conversation completed');
      delete conversations[callSid];
    } else {
      const gather = twiml.gather({
        input: 'speech', action: baseUrl + '/call-agent', method: 'POST',
        speechTimeout: '2', timeout: 10, language: 'en-US',
      });
      gather.pause({ length: 1 });
      gather.say({ voice: 'Polly.Joanna-Neural' }, aiReply);
      twiml.say({ voice: 'Polly.Joanna-Neural' }, 'I did not hear a response. Thank you for your time. Goodbye.');
    }
  } catch (err) {
    console.error('Claude error:', err);
    logToDb(context, callSid, 'ai-failed', 'Technical error: ' + err.message, 'AI conversation failed');
    twiml.say({ voice: 'Polly.Joanna-Neural' }, 'I apologize, I am having a technical issue. Please try again later. Goodbye.');
  }
  callback(null, twiml);
};

function callClaude(apiKey, messages) {
  return new Promise((resolve, reject) => {
    const systemPrompt = 'You are a friendly and professional Medicare care coordinator for StarPulse. You are speaking with a member on the phone about their healthcare gap. Keep responses short (1-3 sentences) since this is a voice conversation. Be warm, empathetic, and helpful. Help them understand why their screening or medication adherence matters, and assist with scheduling if they want. If they want to schedule, offer time slots: tomorrow morning 9 AM, tomorrow afternoon 2 PM, or tomorrow afternoon 3:30 PM. Never provide specific medical diagnoses. End the conversation gracefully when the member is satisfied. Speak naturally and conversationally. Use filler phrases like Sure thing, Let me help with that, That is a great question. Avoid lists or bullet points — use flowing sentences. Keep a warm, unhurried tone.';
    const body = JSON.stringify({ model: 'claude-haiku-4-5', max_tokens: 200, system: systemPrompt, messages: messages });
    const options = {
      hostname: 'api.anthropic.com', path: '/v1/messages', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data).content[0].text); }
        catch (e) { reject(new Error('Parse error: ' + data.substring(0, 200))); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}
"""

# ── Set environment variables (Databricks creds for logging) ────
env_api = f"https://serverless.twilio.com/v1/Services/{SERVICE_SID}/Environments/{ENV_SID}/Variables"
env_vars = {
    "DATABRICKS_HOST": os.environ["DATABRICKS_HOST"].replace("https://", "").rstrip("/"),
    "DATABRICKS_TOKEN": os.environ["DATABRICKS_TOKEN"],
    "DATABRICKS_WAREHOUSE": os.environ["DATABRICKS_WAREHOUSE"],
    "ANTHROPIC_API_KEY": os.environ["ANTHROPIC_API_KEY"],
}
for key, val in env_vars.items():
    # Try create
    resp = requests.post(env_api, auth=auth, data={"Key": key, "Value": val})
    if resp.status_code in (200, 201):
        print(f"Env var {key}: created")
    elif resp.status_code == 409:
        # Already exists — list, find SID, update
        r2 = requests.get(env_api, auth=auth)
        for v in r2.json().get("variables", []):
            if v["key"] == key:
                requests.post(f"{env_api}/{v['sid']}", auth=auth, data={"Value": val})
                print(f"Env var {key}: updated")
                break
    else:
        print(f"Env var {key}: FAILED {resp.status_code} {resp.text[:100]}")

# ── Upload all functions ─────────────────────────────────────────
# Step 1: Create function resources via regular API
# Step 2: Upload versions via upload API
regular_api = f"https://serverless.twilio.com/v1/Services/{SERVICE_SID}"
upload_api = f"https://serverless-upload.twilio.com/v1/Services/{SERVICE_SID}"

functions = {
    "/call-gather": ("call-gather.js", GATHER_CODE),
    "/call-slot": ("call-slot.js", SLOT_CODE),
    "/call-agent": ("call-agent.js", AGENT_CODE),
}

function_version_sids = []

for path, (filename, code) in functions.items():
    # Create the function
    resp = requests.post(
        f"{regular_api}/Functions",
        auth=auth,
        data={"FriendlyName": path.strip("/")},
    )
    if resp.status_code in (200, 201):
        fn_sid = resp.json()["sid"]
        print(f"Created function {path}: {fn_sid}")
    elif resp.status_code == 409:
        # Already exists, list and find it
        resp2 = requests.get(f"{regular_api}/Functions", auth=auth)
        for fn in resp2.json().get("functions", []):
            if fn["friendly_name"] == path.strip("/"):
                fn_sid = fn["sid"]
                print(f"Function {path} already exists: {fn_sid}")
                break
    else:
        print(f"Error creating {path}: {resp.status_code} {resp.text[:200]}")
        continue

    # Upload function version via upload API
    resp = requests.post(
        f"{upload_api}/Functions/{fn_sid}/Versions",
        auth=auth,
        files={"Content": (filename, code.strip(), "application/javascript")},
        data={"Path": path, "Visibility": "public"},
    )
    print(f"  Upload version {path}: HTTP {resp.status_code}")
    if resp.status_code in (200, 201):
        ver_sid = resp.json()["sid"]
        print(f"  Version SID: {ver_sid}")
        function_version_sids.append(ver_sid)
    else:
        print(f"  Error: {resp.text[:200]}")

print(f"\nAll version SIDs: {function_version_sids}")

# ── Create a build ───────────────────────────────────────────────
if len(function_version_sids) == 3:
    build_data = [("FunctionVersions", sid) for sid in function_version_sids]

    resp = requests.post(
        f"https://serverless.twilio.com/v1/Services/{SERVICE_SID}/Builds",
        auth=auth,
        data=build_data,
    )
    print(f"\nBuild: HTTP {resp.status_code}")
    if resp.status_code in (200, 201):
        build = resp.json()
        build_sid = build["sid"]
        print(f"Build SID: {build_sid}")
        print(f"Status: {build['status']}")

        # Wait for build to complete
        for _ in range(20):
            time.sleep(3)
            r = requests.get(
                f"https://serverless.twilio.com/v1/Services/{SERVICE_SID}/Builds/{build_sid}",
                auth=auth,
            )
            status = r.json().get("status", "")
            print(f"  Build status: {status}")
            if status == "completed":
                break
            if status == "failed":
                print(f"  Build FAILED: {r.json()}")
                break

        # Deploy to environment
        if status == "completed":
            r = requests.post(
                f"https://serverless.twilio.com/v1/Services/{SERVICE_SID}/Environments/{ENV_SID}/Deployments",
                auth=auth,
                data={"BuildSid": build_sid},
            )
            print(f"\nDeploy: HTTP {r.status_code}")
            if r.status_code in (200, 201):
                dep = r.json()
                print(f"Deployment SID: {dep['sid']}")
                print(f"\n=== FUNCTIONS LIVE ===")
                print(f"call-gather: https://starpulse-webhooks-1622-prod.twil.io/call-gather")
                print(f"call-slot:   https://starpulse-webhooks-1622-prod.twil.io/call-slot")
                print(f"call-agent:  https://starpulse-webhooks-1622-prod.twil.io/call-agent")
            else:
                print(f"  Deploy error: {r.text[:200]}")
    else:
        print(f"  Build error: {resp.text[:200]}")
else:
    print("Not all functions uploaded successfully")
