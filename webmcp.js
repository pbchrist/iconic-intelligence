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
      "ICONIC learns one business. It records that market every day and keeps the history on hardware Patrick runs. The longer it runs, the more of that market it holds. One private connector is in use for the current client. Patrick sets it up so an AI the owner already uses can read the same memory and the same numbers. There is no public install and no public API. The writing model only sees public listing data. Nothing goes out until Patrick approves it. The Monday, Wednesday and Friday briefings are what the current dealer receives. They are not the whole product.",
    for_whom: "An owner who runs the store: one franchise rooftop or a small dealer group.",
    includes: [
      "A private memory of one market, recorded every day",
      "History kept on hardware Patrick runs",
      "One private connector, set up by Patrick, in use for the current client only",
      "The same memory and the same numbers for the AI that connector serves",
      "Every number tied to a dated public page and the exact quote",
      "No public install and no public API",
      "Running now for one franchise dealer: rival lots read daily, a briefing Monday, Wednesday and Friday mornings, questions by text to a private Telegram bot",
      "Like-for-like comparisons: same year, model, trim, cab, drive and engine, sticker within $1,000",
      "The writing model only sees public listing data",
      "Nothing goes out until Patrick approves it"
    ],
    live_clients: "One franchise auto dealer. Clients are not named. The private connector is in use for that client only. No third-party AI is offered as a public connection.",
    price: "Not listed yet. Ask Patrick.",
    how_to_start: `Email ${EMAIL} with your business, your top three competitors, and what you wish you knew every Monday. Or call ${PHONE}.`
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
        const href = `mailto:${EMAIL}?subject=${encodeURIComponent("Start with one report")}&body=${encodeURIComponent(body)}`;
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
