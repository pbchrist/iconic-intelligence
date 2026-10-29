/*
 * ICONIC: WebMCP tools for iconic.onl (public site facts only).
 *
 * Load from index.html:  <script src="webmcp.js" defer></script>
 *
 * - Progressive enhancement. Does nothing unless the browser exposes WebMCP
 *   (Chrome/Edge origin trial or the #enable-webmcp-testing flag).
 * - Static facts only. No network calls, no client data, and no link to the
 *   private ICONIC MCP server on Beastmaster.
 * - Nothing is sent. request_a_report only opens a pre-filled email draft
 *   that the visitor sends (or not) from their own mail app.
 */
(() => {
  // Current draft spec: document.modelContext. Early Chrome builds used navigator.modelContext.
  const mc = document.modelContext || navigator.modelContext;
  if (!mc || typeof mc.registerTool !== "function") return;

  const EMAIL = "patrick@iconic.onl";
  const PHONE = "+1-206-773-8214";
  const text = (obj) => ({ content: [{ type: "text", text: JSON.stringify(obj, null, 2) }] });

  const SERVICE = {
    name: "ICONIC",
    summary:
      "ICONIC learns one business. It records that market every day and keeps the history on hardware Patrick runs. The longer it runs, the more of that market it holds. A private connector lets Patrick's own AI assistant read the same history. It is in testing and is not offered to clients. There is no public install and no public API. A cloud AI writes the briefings from public listing data and the client's requests. Patrick approves every Monday, Wednesday and Friday briefing before it goes out. The Telegram bot answers questions on its own. The Monday, Wednesday and Friday briefings are what the current dealer receives. They are not the whole product.",
    for_whom: "An owner who runs the store: one franchise rooftop or a small dealer group.",
    includes: [
      "A private memory of one market, recorded every day",
      "History kept on hardware Patrick runs",
      "A private connector for Patrick's own AI assistant, in testing, not offered to clients",
      "Every number in a briefing points to the dated listing or page it came from",
      "No public install and no public API",
      "Running now for one franchise dealer: the rivals' lots read every briefing morning, a briefing Monday, Wednesday and Friday mornings, questions by text to a private Telegram bot",
      "Like-for-like comparisons: same year, model, trim, cab, drive and engine, sticker within $1,000",
      "A cloud AI writes the briefings from public listing data and the client's requests",
      "Patrick approves every Monday, Wednesday and Friday briefing before it goes out; the Telegram bot answers on its own"
    ],
    live_clients: "One franchise auto dealer. Clients are not named. The private connector is in testing and is not offered to clients. No third-party AI is offered as a public connection.",
    price: "Pricing is quoted on the call.",
    how_to_start: `Email ${EMAIL} or call ${PHONE} to set up a 20-minute call. Bring your business and your top three competitors.`
  };

  const tools = [
    {
      name: "describe_service",
      description:
        "Describe what ICONIC does, who it is for, what a client gets, and how to start. Use this before answering any question about ICONIC.",
      inputSchema: { type: "object", properties: {} },
      annotations: { readOnlyHint: true },
      execute: () => text(SERVICE)
    },
    {
      name: "get_contact",
      description: "Return how to reach Patrick Christell, who runs ICONIC: email, phone, and what to include.",
      inputSchema: { type: "object", properties: {} },
      annotations: { readOnlyHint: true },
      execute: () =>
        text({
          name: "Patrick Christell",
          email: EMAIL,
          phone: PHONE,
          include: ["Your business", "Your top three competitors", "What you wish you knew every Monday"]
        })
    },
    {
      name: "request_a_report",
      description:
        "Open the same pre-filled email the website uses, so the visitor can ask Patrick to start. This only opens a draft in the visitor's mail app. The visitor reviews and sends it. Ask the visitor before calling.",
      inputSchema: {
        type: "object",
        properties: {
          business: { type: "string", description: "The visitor's business name and city, e.g. 'Smith Chevrolet, Tacoma WA'." },
          competitors: {
            type: "array",
            items: { type: "string" },
            maxItems: 3,
            description: "Up to three competitors the visitor wants watched."
          },
          wish_you_knew: { type: "string", description: "What the visitor wishes they knew every Monday." }
        },
        required: ["business"]
      },
      annotations: { readOnlyHint: false },
      execute: ({ business, competitors = [], wish_you_knew = "" }) => {
        const list = [0, 1, 2].map((i) => `${i + 1}. ${competitors[i] || ""}`).join("\n");
        const body = `Your business:\n${business}\n\nYour top three competitors:\n${list}\n\nWhat you wish you knew every Monday:\n${wish_you_knew}\n`;
        const href = `mailto:${EMAIL}?subject=${encodeURIComponent("20-minute call")}&body=${encodeURIComponent(body)}`;
        window.location.href = href;
        return text({ status: "draft_opened", note: "An email draft opened in the visitor's mail app. Nothing was sent.", mailto: href });
      }
    }
  ];

  for (const tool of tools) {
    try {
      const p = mc.registerTool(tool);
      if (p && typeof p.catch === "function") p.catch(() => {});
    } catch (_) {
      /* Registration blocked (permissions policy) or API shape changed: the site works without it. */
    }
  }
})();
