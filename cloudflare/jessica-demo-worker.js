export default {
  async fetch(request, env) {
    // CORS headers for GitHub Pages
    const corsHeaders = {
      'Access-Control-Allow-Origin': 'https://thecalltaker.com',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    // Rate limiting: 3 requests per IP per hour
    const ip = request.headers.get('CF-Connecting-IP');
    const rateLimitKey = `rate:${ip}`;
    const count = await env.DEMO_KV.get(rateLimitKey);
    if (count && parseInt(count) >= 3) {
      return new Response(
        JSON.stringify({ error: 'rate_limited' }),
        { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' }}
      );
    }
    await env.DEMO_KV.put(rateLimitKey, String((parseInt(count) || 0) + 1), { expirationTtl: 3600 });

    // Parse business name
    const { businessName } = await request.json();
    const safeName = (businessName || 'your business')
      .replace(/[<>"']/g, '')
      .substring(0, 50);

    // Jessica's greeting script
    const script = `Thank you for calling ${safeName}, this is Jessica! We're so glad you reached out. I can help you schedule an appointment, answer questions about our services, or connect you with the right person. What can I help you with today?`;

    // Call ElevenLabs Flash v2.5
    const elevenResponse = await fetch(
      'https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM/stream',
      {
        method: 'POST',
        headers: {
          'xi-api-key': env.ELEVENLABS_API_KEY,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: script,
          model_id: 'eleven_flash_v2_5',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75,
          },
        }),
      }
    );

    if (!elevenResponse.ok) {
      return new Response(
        JSON.stringify({ error: 'tts_failed' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' }}
      );
    }

    // Stream audio back
    return new Response(elevenResponse.body, {
      headers: {
        ...corsHeaders,
        'Content-Type': 'audio/mpeg',
      },
    });
  },
};
