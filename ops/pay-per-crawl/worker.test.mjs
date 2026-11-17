import { test } from "node:test";
import assert from "node:assert/strict";
import worker, {classify} from "./worker.mjs";

const URL = "https://iconic.onl/research/dealership-pricing-intelligence/";
const LIVE = {AIPAYGEN_MODE:"charge",AIPAYGEN_GATEWAY_ID:"3f9a1c0b7d2e",AIPAYGEN_SECRET:"private-test-secret"};
const mk = (ua="Mozilla/5.0",path=URL,extras={}) => new Request(path,{headers:{"user-agent":ua,...extras}});
async function withFetch(handler, task) {
  const original=globalThis.fetch;
  globalThis.fetch=handler;
  try { return await task(); }
  finally { globalThis.fetch=original; }
}

test("normal visitors use origin without requesting payment",async()=>{
  const req=mk();
  await withFetch(async input=>{assert.equal(input,req);return new Response("public",{status:200})},
    async()=>assert.equal((await worker.fetch(req,LIVE)).status,200));
});
test("all search/answer crawlers keep free access",async()=>{
  for(const ua of ["Googlebot","Bingbot","OAI-SearchBot","ChatGPT-User","Claude-SearchBot","Claude-User","PerplexityBot","Perplexity-User","Applebot"]) {
    const req=mk(ua); assert.equal(classify(req),null,ua);
    await withFetch(async input=>{assert.equal(input,req);return new Response("free",{status:200})},
      async()=>assert.equal((await worker.fetch(req,LIVE)).status,200));
  }
});
test("known training crawler gets gateway challenge and path preserved",async()=>{
  const req=mk("GPTBot/1.0",URL+"?format=html");
  await withFetch(async (url,options)=>{
    assert.equal(url,"https://aipaygen.com/g/3f9a1c0b7d2e/research/dealership-pricing-intelligence/?format=html");
    assert.equal(options.headers.get("user-agent"),"GPTBot/1.0");
    assert.equal(options.headers.get("authorization"),null);
    return new Response('{"x402Version":2}',{status:402});
  },async()=>assert.equal((await worker.fetch(req,LIVE)).status,402));
});
test("ClaudeBot, CCBot, and Bytespider are classified",()=>{
  for(const ua of ["ClaudeBot/1.0","CCBot/2.0","Bytespider"]) assert.ok(classify(mk(ua)));
});
test("homepage, research index, sitemap, assets and other services remain free",()=>{
  for(const path of ["/","/research/","/research/research.css","/robots.txt","/sitemap.xml","/llms.txt","/ai/services.md","/agents/marketplace/"]) {
    assert.equal(classify(mk("GPTBot/1.0","https://iconic.onl"+path)),null,path);
  }
});
test("charge mode without gateway/secret is inert",async()=>{
  const req=mk("GPTBot/1.0");
  await withFetch(async input=>{assert.equal(input,req);return new Response("public",{status:200})},
    async()=>assert.equal((await worker.fetch(req,{AIPAYGEN_MODE:"charge"})).status,200));
});
test("off mode is inert",async()=>{
  const req=mk("GPTBot/1.0");
  await withFetch(async input=>{assert.equal(input,req);return new Response("public",{status:200})},
    async()=>assert.equal((await worker.fetch(req,LIVE && {AIPAYGEN_MODE:"off",...LIVE,AIPAYGEN_MODE:"off"})).status,200));
});
test("gateway can retrieve origin content only with matching secret",async()=>{
  const req=mk("GPTBot/1.0",URL,{"x-aipaygen-gateway-secret":"private-test-secret"});
  await withFetch(async input=>{assert.equal(input,req);return new Response("origin",{status:200})},
    async()=>assert.equal((await worker.fetch(req,LIVE)).status,200));
});
test("bad secret is not accepted",async()=>{
  const req=mk("GPTBot/1.0",URL,{"x-aipaygen-gateway-secret":"wrong"});
  await withFetch(async (url)=>{assert.equal(typeof url,"string");return new Response("pay",{status:402})},
    async()=>assert.equal((await worker.fetch(req,LIVE)).status,402));
});
test("paid retry goes to gateway for signature verification, never straight to origin",async()=>{
  const req=mk("Mozilla/5.0",URL,{"payment-signature":"signed-test-payload"});
  await withFetch(async (url,options)=>{
    assert.ok(String(url).startsWith("https://aipaygen.com/g/"));
    assert.equal(options.headers.get("payment-signature"),"signed-test-payload");
    return new Response("paid",{status:200});
  },async()=>assert.equal((await worker.fetch(req,LIVE)).status,200));
});
test("observe mode does not return 402",async()=>{
  const req=mk("GPTBot/1.0");
  await withFetch(async input=>{assert.equal(input,req);return new Response("public",{status:200})},
    async()=>assert.equal((await worker.fetch(req,{...LIVE,AIPAYGEN_MODE:"observe"})).status,200));
});
test("gateway outages fail closed only for charged crawlers",async()=>{
  const req=mk("GPTBot/1.0");
  await withFetch(async()=>{throw new Error("offline")},async()=>assert.equal((await worker.fetch(req,LIVE)).status,503));
});
test("gateway redirects are refused",async()=>{
  const req=mk("GPTBot/1.0");
  await withFetch(async()=>new Response(null,{status:302,headers:{location:"https://evil.example/"}}),
    async()=>assert.equal((await worker.fetch(req,LIVE)).status,502));
});
