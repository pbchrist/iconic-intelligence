// ICONIC pay-per-crawl edge adapter. Read README.md before enabling.
// GitHub Pages cannot run middleware: this is for a reverse proxy/Cloudflare Worker route.
const TRAINING_BOTS = [
  ["GPTBot", /(?:^|\W)GPTBot(?:\W|$)/i],
  ["ClaudeBot", /(?:^|\W)ClaudeBot(?:\W|$)/i],
  ["CCBot", /(?:^|\W)CCBot(?:\W|$)/i],
  ["Bytespider", /(?:^|\W)Bytespider(?:\W|$)/i],
];
const FREE_SEARCH_BOTS = /Googlebot|Bingbot|OAI-SearchBot|ChatGPT-User|Claude-SearchBot|Claude-User|PerplexityBot|Perplexity-User|Applebot|DuckAssistBot/i;
const STATIC = /\.(?:css|js|mjs|map|svg|png|jpe?g|webp|avif|gif|ico|woff2?|ttf|xml|txt)$/i;

export function classify(request) {
  const url = new URL(request.url);
  if (request.method !== "GET" || !["iconic.onl", "www.iconic.onl"].includes(url.hostname)) return null;
  if (!url.pathname.startsWith("/research/") || url.pathname === "/research/" || url.pathname === "/research/index.html" || STATIC.test(url.pathname)) return null;
  const ua = request.headers.get("user-agent") || "";
  if (FREE_SEARCH_BOTS.test(ua)) return null;
  for (const [name, pattern] of TRAINING_BOTS) if (pattern.test(ua)) return name;
  return null;
}

function gatewayUrl(request, gatewayId) {
  if (!/^[A-Za-z0-9_-]{8,80}$/.test(String(gatewayId || ""))) throw new Error("Unconfigured gateway ID");
  const url = new URL(request.url);
  // Keep the original path/query, never forward a client-chosen upstream or host.
  return "https://aipaygen.com/g/" + gatewayId + url.pathname + url.search;
}

export default {
  async fetch(request, env = {}, ctx = {}) {
    const mode = env.AIPAYGEN_MODE || "off";
    const bot = classify(request);
    // Pass through all humans, search/answer bots, discovery files and non-research routes.
    // Once paid, AIPayGen fetches the original URL with this confidential secret header.
    if (env.AIPAYGEN_SECRET &&
        request.headers.get("x-aipaygen-gateway-secret") === env.AIPAYGEN_SECRET) {
      return fetch(request);
    }
    const paidRetry = !!(request.headers.get("payment-signature") || request.headers.get("x-payment"));
    if (!bot && !paidRetry) return fetch(request);
    if (mode === "observe") {
      if (bot) console.info(JSON.stringify({event:"ai_crawler_observed",bot,path:new URL(request.url).pathname}));
      return fetch(request);
    }
    // No live monetization until a gateway ID AND a private origin-bypass secret are installed.
    if (mode !== "charge" || !env.AIPAYGEN_GATEWAY_ID || !env.AIPAYGEN_SECRET) return fetch(request);
    if (!bot && paidRetry && !new URL(request.url).pathname.startsWith("/research/")) return fetch(request);
    const headers = new Headers();
    for (const key of ["user-agent","accept","payment-signature","x-payment"]) {
      const value = request.headers.get(key);
      if (value) headers.set(key, value);
    }
    try {
      const reply = await fetch(gatewayUrl(request, env.AIPAYGEN_GATEWAY_ID), {
        method:"GET",headers,redirect:"manual"
      });
      // Keep buyers from following untrusted redirects; do not silently serve paid content free.
      if (reply.status >= 300 && reply.status < 400) {
        return new Response("Payment gateway redirect refused", {status:502,headers:{"cache-control":"no-store"}});
      }
      return reply;
    } catch {
      return new Response("Payment gateway temporarily unavailable", {
        status:503, headers:{"cache-control":"no-store","retry-after":"60"}
      });
    }
  }
};
