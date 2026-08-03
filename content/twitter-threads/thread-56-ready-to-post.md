# Twitter Thread — September 25, 2026
## Topic: I Built an Agent That Passes the "Mom Test." Here's What That Means.
## Status: READY TO POST

---

**Tweet 1/8 (Hook):**
```
The "Mom Test":

Can my mom use your agent without asking for help?

Not my engineer friend.
Not my tech-savvy colleague.
My mom.

If she can't, your agent isn't ready.

Here's how I built one that passes 🧵
```

**Tweet 2/8:**
```
The problem:

Most agents are built by engineers.
For engineers.

Result:
→ API keys required
→ JSON responses
→ Terminal interfaces
→ Error messages in logs

My mom:
→ Doesn't know what an API is
→ Wants a chat interface
→ Needs clear answers
→ Gets frustrated by errors

Your users are my mom.
```

**Tweet 3/8:**
```
Test 1: Setup

❌ Bad:
"Clone this repo, install Python, set environment variables, run docker-compose..."

✅ Good:
"Go to this website. Type your question. That's it."

The agent should work with zero setup.
Not minimal setup.
Zero.
```

**Tweet 4/8:**
```
Test 2: Interface

❌ Bad:
```
POST /api/v1/agent
Body: {"query": "hello", "context": {...}}
```

✅ Good:
→ Chat window
→ Type message
→ Press enter
→ Get answer

If it needs a POST request, it's not passing the Mom Test.
```

**Tweet 5/8:**
```
Test 3: Error Handling

❌ Bad:
"Error 500: Internal Server Error"
"Traceback (most recent call last):..."
"JSONDecodeError: Expecting value"

✅ Good:
"I couldn't find that information. Could you try rephrasing?"
"I'm having trouble connecting. Let me try again..."
"I'm not sure about that, but here's what I do know..."

Errors should be friendly.
Not technical.
```

**Tweet 6/8:**
```
Test 4: Expectations

❌ Bad:
Agent claims to know everything.
Then fails on simple questions.
User feels lied to.

✅ Good:
"I can help with X, Y, and Z."
"For other topics, I might not have the answer."
"Let me connect you with a human for this."

Set expectations clearly.
Under-promise, over-deliver.
```

**Tweet 7/8:**
```
Test 5: Trust

❌ Bad:
→ No sources cited
→ No confidence shown
→ No way to verify
→ Black box

✅ Good:
→ "According to [source]..."
→ "I'm 85% confident about this..."
→ "You can verify this at [link]"
→ "Here's how I arrived at this answer..."

Trust is earned through transparency.
```

**Tweet 8/8 (CTA):**
```
The Mom Test is the real test.

Technical users will tolerate complexity.
Regular users won't.

Build for my mom.
Not for Hacker News.

The framework:
→ github.com/ArQon-ai/agentstack

With:
→ Simple interfaces
→ Friendly errors
→ Clear expectations
→ Built-in trust

Would your agent pass the Mom Test? 👇
```

---

*Generated autonomously by ArQon Agentics — September 25, 2026*
