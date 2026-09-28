#!/usr/bin/env node
// gochina.events — static build (v2: trust-first, deep industries/shows).
import { mkdirSync, rmSync, writeFileSync, readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  SITE, INDUSTRIES, SERVICES, TRADE_SHOWS, TRIPS, GUIDES,
} from "./src/content.mjs";
import { GUIDE_BODIES } from "./src/guides.mjs";
import { SHOW_VERIFIED, INDUSTRY_DEEP, PRICING_EXAMPLES } from "./src/deep.mjs";
import { POSTS } from "./src/blog.mjs";
import { SVC_ORDER } from "./src/content.mjs";
import { PHOTOS } from "./src/photos.mjs";
import {
  page, pageZh, esc, li, cards, breadcrumbJsonLd, serviceJsonLd,
} from "./lib/layout.mjs";
import { buyerForm, meetupsForm, formScript } from "./lib/forms.mjs";
import { supplierFormZh, localServiceFormZh, sponsorshipFormZh, zhFormScript } from "./lib/forms-zh.mjs";

const ROOT = decodeURIComponent(fileURLToPath(new URL(".", import.meta.url)));
const OUT = `${ROOT}site`;
const D = SITE.domain;

rmSync(OUT, { recursive: true, force: true });

const fileWith = (rel, html) => {
  const p = `${OUT}/${rel}`;
  mkdirSync(p.slice(0, p.lastIndexOf("/")), { recursive: true });
  writeFileSync(p, html);
};

const S = `<script>${formScript}</script>`;
const finalScript = () => S;

const trialNotice = `
<div class="notice"><p><strong>Early-stage service:</strong> goChina Events launched its site newly. Every enquiry gets a human reply, and we are happy to do your first verification call before any payment — we are working to earn trust, not assume it.</p></div>`;

/* ------------------------------------------------------------------ home */
const upcomingShows = TRADE_SHOWS.filter((s) => SHOW_VERIFIED[s.slug]);
fileWith("index.html", page({
  title: "China Trade Show Support & Sourcing Trips — goChina Events",
  description: "Local, English-speaking support for overseas buyers in China: trip planning, interpreters, supplier shortlists, factory visits and follow-up. Serving Guangzhou–Foshan and Shanghai.",
  canonical: `${D}/`,
  trail: [],
  showCrumbs: false,
  body: `
<section class="hero">
  <h1>Build your China supply chain — from first research to shipped orders</h1>
  <p class="lead">We help <strong>overseas companies develop and run China supply chains</strong>: supplier research and vetting, quote comparison at your quantity, coordinated factory audits, sample-round management, order milestones and pre-shipment inspection — <strong>most of it remote from day one</strong>, with an on-the-ground team in Guangzhou-Foshan and Shanghai when you visit.</p>
  <p><a class="btn" href="/plan-your-trip/">Start a project</a> <a class="btn ghost" href="/how-it-works/">How it works</a></p>
</section>
<div class="cols">
<div>
<ul class="clean">${li([
    "<strong>Remote & day-one:</strong> shortlists, evidence notes and priced comparisons while your project is still on a spreadsheet.",
    "<strong>Gate-keeping:</strong> samples, audits and milestones coordinated — invoices and contracts stay between you and the supplier.",
    "<strong>Honest edges:</strong> we do not certify quality, take ownership of goods, or guarantee orders. That is documented on our <a href='/commercial-disclosure/'>disclosure page</a>.",
  ])}</ul>
</div>
<div>
<ul class="clean">${li([
    "<strong>On the ground in Guangzhou-Foshan & Shanghai:</strong> accompanied factory and showroom days, interpreters by category.",
    "<strong>Reaching you where you start</strong>: many buyers find us through trade fair weeks — <a href='/trade-shows/'>see the fairs we support</a> — then stay for the supply-chain work.",
    "<strong>Two engagement modes</strong>: remote programs (research, coordination, inspection-driving) and China visit days.",
  ])}</ul>
</div>
</div>

<h2>Start where your supply chain actually starts</h2>
${cards([
  { href: "/services/supplier-research/", h: "1. Research & vet suppliers", d: "Evidence-based shortlists at your quantity — remotely, before you book any flight." },
  { href: "/services/purchasing-coordination/", h: "2. Manage quotes, samples & orders", d: "Milestones, sample rounds, document checks — momentum without another trip." },
  { href: "/services/inspection-logistics-coordination/", h: "3. Inspect & ship", d: "Accredited inspection and freight coordination, third parties at actual rates." },
  { href: "/services/factory-visits/", h: "4. Visit & audit on the ground", d: "Accompanied factory and showroom days in Guangzhou-Foshan and Shanghai." },
], (c) => `<div class="card"><h3><a href="${c.href}">${esc(c.h)}</a></h3><p>${esc(c.d)}</p></div>`)}
<h2>Trade fairs — one of the ways buyers reach us</h2>
<p>We support the major sourcing fairs (dates verified from official pages where available) — useful as an entry point for a first visit, and frequently the moment a supply-chain project starts. Shows are an entry channel for us, not the business itself: <a href="/trade-shows/">see the fairs we support</a>.</p>
<h2>Industries we cover for overseas buyers</h2>
${cards(INDUSTRIES, (i) => `<div class="card"><h3><a href="/industries/${i.slug}/">${esc(i.name)}</a></h3><p>${esc(i.short)}</p></div>`)}
<h2>Three trips we design</h2>
${cards(TRIPS, (t) => `
  <div class="card"><h3><a href="/business-trips/${t.slug}/">${esc(t.name)}</a></h3><p>${esc(t.days)} · ${esc(t.cities)}</p>
  <div class="meta">${t.status === "active" ? "Live offer — scopeable now" : "Sample structure — priced after availability check"}</div></div>`)}
<h2>How your trip actually runs</h2>
<table>
<tr><th>Step</th><th>What happens</th></tr>
<tr><td>1. Enquiry</td><td>You send what you have — dates, categories, quantities. We reply with questions or an honest "this one you can do alone, here's why."</td></tr>
<tr><td>2. Plan</td><td>Requirement brief, supplier shortlist with what we actually verified, visit route, hotel options.</td></tr>
<tr><td>3. In China</td><td>Accompanied visits with industry interpreters; same-evening notes of every meeting.</td></tr>
<tr><td>4. After you fly</td><td>Quote chasing, sample loops, third-party inspection and freight coordinated — documented.</td></tr>
</table>
<h2>What you can check, without trusting us</h2>
<div class="cols">
<div>
<ul class="clean">${li([
    "One scheduled call before any payment — ask anything, bring your itinerary.",
    "<a href='/templates/'>Sample files</a>: our trip plan, supplier comparison sheet, factory-visit checklist and meeting-notes format.",
    "<a href='/pricing/'>Pricing structure</a>: what is a fixed fee, what is pass-through cost, what you can cancel.",
  ])}</ul>
</div>
<div>
<ul class="clean">${li([
    "<a href='/commercial-disclosure/'>Commercial disclosure</a>: who pays us, when, and how recommendations stay independent.",
    "We are an independent service provider — not a fair organizer, not a ticket reseller.",
    "No ratings or testimonials published yet; we'd rather show method than invented praise.",
  ])}</ul>
</div>
</div>
${trialNotice}
${buyerForm({ heading: "Plan My Trip" })}
${finalScript()}`,
}));

/* ------------------------------------------------------------ trade shows */
fileWith("trade-shows/index.html", page({
  title: "China Trade Shows for Overseas Buyers — Verified Info & Visit Support",
  description: "China trade fairs for overseas buyers — dates verified against official organizer pages where available. Support: trip plans, interpreters, supplier visits around each fair.",
  canonical: `${D}/trade-shows/`,
  trail: [["goChina Events", "/"], ["Trade Shows"]],
  body: `
<h1>Trade shows we support</h1>
<p>Each page states what matters for <em>your trip</em>: verified next-edition dates where we have them (source-linked), who the fair suits, and what visit support we can arrange around it. Dates not yet re-verified for the current session say so plainly — we never guess dates.</p>
<div class="cards">
${TRADE_SHOWS.map((s) => {
  const v = SHOW_VERIFIED[s.slug];
  return `
  <div class="card">
    <h3><a href="/trade-shows/${s.slug}/">${esc(s.name)}</a></h3>
    <p>${esc(s.city)}${v ? ` · <strong>${esc(v.nextEdition)}</strong>` : ` · ${esc(s.cadence)}`}</p>
    <div class="meta">${v ? "Dates verified from official source" : "Dates: check official site — we confirm per trip"}</div>
  </div>`;
}).join("")}
</div>
${buyerForm({ compact: true, heading: "Enquiry — tell us which show" })}
${finalScript()}`,
}));

for (const s of TRADE_SHOWS) {
  const v = SHOW_VERIFIED[s.slug] || null;
  const eventLd = v
    ? [{
        "@context": "https://schema.org", "@type": "Event",
        name: `${s.name} (${v.nextEdition.split(":")[0].trim()})`,
        startDate: SHOW_VERIFIED[s.slug].startDate,
        eventStatus: "https://schema.org/EventScheduled",
        location: {
          "@type": "Place",
          name: v.venueExact,
          address: s.city.split(",")[0].trim(),
        },
        organizer: { "@id": `${D}/trade-shows/${s.slug}/#official-organizer` },
      }]
    : [];
  if (eventLd.length) {
    eventLd[0].organizer = { "@type": "Organization", "@id": `${D}/#official-organizer-${s.slug}`, name: "Official fair organizer — see source link on page" };
  }
  // FAQPage schema only where real answers exist on the page
  const faqLd = v && v.faqs && v.faqs.length
    ? [{
        "@context": "https://schema.org", "@type": "FAQPage",
        mainEntity: v.faqs.map(([q, a]) => ({
          "@type": "Question", name: q,
          acceptedAnswer: { "@type": "Answer", text: a },
        })),
      }]
    : [];
  fileWith(`trade-shows/${s.slug}/index.html`, page({
    title: `${s.name} — Visitor Support & Sourcing Trip Planning`,
    description: v
      ? `${s.name}: ${v.nextEdition}, ${v.venueExact}. Visit support for overseas buyers: interpreting, supplier visits around the fair in ${s.city.split(",")[0]}.`
      : `${s.name}. Planning facts plus visit support for overseas buyers: interpreting, supplier visits around ${s.city.split(",")[0]}.`,
    canonical: `${D}/trade-shows/${s.slug}/`,
    trail: [["goChina Events", "/"], ["Trade Shows", "/trade-shows/"], [s.name || s.name]],
    extraJsonLd: [
      breadcrumbJsonLd([["Home", "/"], ["Trade Shows", "/trade-shows/"], [s.name, null]]),
      ...eventLd,
      ...faqLd,
    ],
    body: `
<h1>${esc(s.name)}</h1>
${v ? `
<table>
<tr><td>Next edition</td><td><strong>${esc(v.nextEdition)}</strong></td></tr>
<tr><td>Venue</td><td>${esc(v.venueExact)}</td></tr>
<tr><td>Phases / key sections</td><td>${esc(v.phasesExact)}</td></tr>
<tr><td>Source</td><td><a href="${esc(v.source)}" rel="noopener" target="_blank">official organizer page</a> · last verified ${esc(v.lastVerified)}</td></tr>
</table>` : `
<table>
<tr><td>City</td><td>${esc(s.city)}</td></tr>
<tr><td>Venue</td><td>${esc(s.venue)}</td></tr>
<tr><td>Cadence</td><td>${esc(s.cadence)}</td></tr>
<tr><td>Next session</td><td><em>Not re-verified for the current session here — check the organizer page. We confirm exact dates with you during planning.</em></td></tr>
<tr><td>Source</td><td><a href="${esc(s.official)}" rel="noopener" target="_blank">official organizer website</a></td></tr>
</table>`}
<div class="notice"><p>goChina Events is an independent service provider — not affiliated with this fair's organizer and not a registration reseller. Official registration: ${v ? `<a href="${esc(v.registrationLink)}" rel="noopener" target="_blank">${esc(v.registrationLink.replace(/^https?:\/\/(www\.)?/, "").slice(0, 40))}…</a>` : `<a href="${esc(s.official)}" rel="noopener" target="_blank">organizer website</a>`}.</p></div>
<h2>Who should go</h2>
<p>${esc(s.whyFits)}${v ? ` ${esc(v.buyersFit)}` : ""}</p>
${v ? `<h3>Suggested arrival</h3><p>${esc(v.arrivalAdvice)}</p>
<h2>Supplier districts worth combining with the fair</h2><p>${esc(v.nearbyClusters)}</p>` : ""}
<h2>What goChina Events does around this show</h2>
<p>${esc(s.supportNote)}</p>
${v ? `<h3>Questions buyers actually ask</h3><ul class="clean">${li(v.faqs.map(([q, a]) => `<strong>${esc(q)}</strong><br>${esc(a)}`))}</ul>` : ""}
<p>Related: ${INDUSTRIES.filter((i) => i.shows.includes(s.slug)).map((i) => `<a href="/industries/${i.slug}/">${esc(i.name)}</a>`).join(" · ") || "see <a href='/services/'>all services</a>."}</p>
${buyerForm({ ctx: { show: s.name, source: `/trade-shows/${s.slug}/` }, compact: true })}
${finalScript()}`,
  }));
}

/* ------------------------------------------------------------ industries */
fileWith("industries/index.html", page({
  title: "Sourcing Industries We Support — From Furniture to Electronics",
  description: "Eight industries for overseas buying trips: furniture & building materials, hospitality equipment, beauty packaging, pet products, automotive aftermarket, machinery, fashion & textiles, consumer electronics.",
  canonical: `${D}/industries/`,
  trail: [["goChina Events", "/"], ["Industries"]],
  body: `
<h1>Industries</h1>
<p>Each page answers the questions buyers in that category really ask — where suppliers cluster, how sampling and MOQs work, what goes wrong, and what we actually check on-site.</p>
${cards(INDUSTRIES, (i) => `<div class="card"><h3><a href="/industries/${i.slug}/">${esc(i.name)}</a></h3><p>${esc(i.short)}</p></div>`)}
${trialNotice}`,
}));

for (const ind of INDUSTRIES) {
  const deep = INDUSTRY_DEEP[ind.slug] || {};
  const showLinks = (deep.showLinks || ind.shows).map((s2) => {
    const sh = TRADE_SHOWS.find((x) => x.slug === s2);
    return sh ? `<a href="/trade-shows/${sh.slug}/">${esc(sh.name)}</a>` : "";
  }).filter(Boolean).join(" · ") || "see <a href='/trade-shows/'>trade shows</a>";
  fileWith(`industries/${ind.slug}/index.html`, page({
    title: `Sourcing ${ind.name} in China — Visit Routes, MOQs & Screening`,
    description: `${ind.short}. Where suppliers cluster, how MOQs and sampling work, what we check on factory visits — for overseas buyers.`,
    canonical: `${D}/industries/${ind.slug}/`,
    trail: [["goChina Events", "/"], ["Industries", "/industries/"], [ind.name]],
    extraJsonLd: [breadcrumbJsonLd([["Home", "/"], ["Industries", "/industries/"], [ind.name, null]])],
    body: `
<h1>${esc(ind.name)}</h1>
<p class="lead">${esc(ind.short)}</p>
<h2>Who we work with here</h2>
<ul class="clean">${li(ind.buyerFit)}</ul>
<h2>What buyers in this category usually ask</h2>
<ul class="clean">${li(deep.buyerQuestions || [])}</ul>
<h2>MOQs, sampling & typical lead times</h2>
<p>${esc(deep.moqSampling || "")}</p>
<h2>What we screen for</h2>
<p>${esc(deep.screeningPoints || ind.sourcingNotes)}</p>
<h2>What gets checked on-site</h2>
<ul class="clean">${li(deep.factoryChecks || [])}</ul>
<h2>Where it goes wrong</h2>
<p>${esc(deep.commonRisks || "")}</p>
<h2>Supplier districts</h2>
<p>${esc(deep.clusters || "")}</p>
<h2>Sample visit route</h2>
<div class="notice"><p>Illustrative structure — real routes are confirmed against your product list and each supplier's availability. ${esc(deep.sampleRoute || "")}</p></div>
<h2>Fairs this industry revolves around</h2>
<p>${showLinks}</p>
<p style="color:#6b7683;font-size:.9rem">${esc(deep.expectedStandard || "")}</p>
${buyerForm({ ctx: { industry: `industry: ${ind.name}`, source: `/industries/${ind.slug}/` }, compact: true })}
${finalScript()}`,
  }));
}

/* -------------------------------------------------------------- services */
fileWith("services/index.html", page({
  title: "Services — Show Support, Interpreters, Supplier Visits & Follow-Up",
  description: "Nine practical services for overseas buyers in China: transfers, vehicles, hotels, interpreters, show support, supplier research, factory visits, purchasing coordination, inspection & freight.",
  canonical: `${D}/services/`,
  trail: [["goChina Events", "/"], ["Services"]],
  body: `
<h1>Services</h1>
<p>Use one, or combine them into a priced trip. Each page states what's in, what's out, and how it's quoted.</p>
${cards(SERVICES, (v) => `<div class="card"><h3><a href="/services/${v.slug}/">${esc(v.name)}</a></h3><p>${esc(v.short)}</p></div>`)}
${trialNotice}`,
}));

for (const v of SERVICES) {
  fileWith(`services/${v.slug}/index.html`, page({
    title: `${v.name} in China — Included, Not Included & How It's Quoted`,
    description: `${v.short}. For overseas trade show and sourcing visitors.`,
    canonical: `${D}/services/${v.slug}/`,
    trail: [["goChina Events", "/"], ["Services", "/services/"], [v.name]],
    extraJsonLd: [
      breadcrumbJsonLd([["Home", "/"], ["Services", "/services/"], [v.name, null]]),
      serviceJsonLd({ name: `${v.name} (China)`, description: v.short, url: `${D}/services/${v.slug}/`, serviceType: v.name }),
    ],
    body: `
<h1>${esc(v.name)}</h1>
<p class="lead">${esc(v.short)}</p>
<h2>Who this is for</h2><p>${esc(v.audience)}</p>
<div class="cols">
  <div><h3>Included</h3><ul class="clean">${li(v.includes)}</ul></div>
  <div><h3>Not included</h3><ul class="clean">${li(v.excludes)}</ul></div>
</div>
<h2>Quote basis</h2><p>${esc(v.pricingNote)}</p>
<p>Structure, examples and pass-through rules: see <a href="/pricing/">pricing & fees</a>.</p>
${buyerForm({ ctx: { service: v.name, source: `/services/${v.slug}/` }, compact: true })}
${finalScript()}`,
  }));
}

/* --------------------------------------------------------- business trips */
fileWith("business-trips/index.html", page({
  title: "Business Trips — Show Support, Sourcing Days, Sample Structures",
  description: "Support packages for China sourcing trips: fair support, supplier-visit trips. Live offers vs sample structures labeled clearly.",
  canonical: `${D}/business-trips/`,
  trail: [["goChina Events", "/"], ["Business Trips"]],
  body: `
<h1>Business trips</h1>
<p>Each trip page says plainly whether it is a <strong>live offer</strong> (scopeable now) or a <strong>sample structure</strong> (real routes, confirmed against availability before any booking or payment).</p>
${cards(TRIPS, (t) => `
  <div class="card"><h3><a href="/business-trips/${t.slug}/">${esc(t.name)}</a></h3><p>${esc(t.days)} · ${esc(t.cities)}</p>
  <div class="meta">${t.status === "active" ? "Live offer — scopeable now" : "Sample structure — priced per trip"}</div></div>`)}
<p>Budget shapes without committed amounts: <a href="/pricing/">pricing page</a>.</p>
${buyerForm({ compact: true, heading: "Enquiry — which trip fits you?" })}
${finalScript()}`,
}));

for (const t of TRIPS) {
  fileWith(`business-trips/${t.slug}/index.html`, page({
    title: `${t.name} — ${t.status === "active" ? "Support Package" : "Sample Structure"}`,
    description: `${t.audience} ${t.days}.`,
    canonical: `${D}/business-trips/${t.slug}/`,
    trail: [["goChina Events", "/"], ["Business Trips", "/business-trips/"], [t.name]],
    body: `
<h1>${esc(t.name)}</h1>
<p>${esc(t.days)} · ${esc(t.cities)}</p>
${t.status === "active"
  ? `<p><strong>Live offer.</strong></p>`
  : `<div class="notice"><p><strong>Sample structure.</strong> The route shows how we plan; actual supplier visits are confirmed before any booking or payment.</p></div>`}
<h2>Who it's for</h2><p>${esc(t.audience)}</p>
<h2>Included</h2><ul class="clean">${li(t.whatIsIncluded)}</ul>
<h2>Quote basis</h2><p>${esc(t.quoteBasis)} See <a href="/pricing/">pricing</a> and <a href="/cancellations/">cancellations</a>.</p>
${buyerForm({ ctx: { source: `/business-trips/${t.slug}/` }, compact: true })}
${finalScript()}`,
  }));
}

/* ---------------------------------------------------------- buyer meetups */
fileWith("buyer-meetups/index.html", page({
  title: "Buyer Meetups Around China's Trade Fairs — Interest List",
  description: "Small-format evening meetups around major China trade fairs for overseas buyers. No confirmed events yet — interest list only; invitations match your categories and dates.",
  canonical: `${D}/buyer-meetups/`,
  trail: [["goChina Events", "/"], ["Buyer Meetups"]],
  body: `
<h1>Buyer meetups</h1>
<p>We are building small evening events around major fairs: a curated table of overseas buyers, matched with a small number of selected Chinese suppliers, in a format without the sales swarm.</p>
<div class="notice"><p><strong>Status:</strong> no event dates, venues or confirmed attendee numbers exist yet, so none are published. Sponsorship is only offered after real buyer attendance is confirmed — we do not pre-sell unconfirmed seats.</p></div>
${meetupsForm()}
${finalScript()}`,
}));

fileWith("buyer-meetups/sponsorship/index.html", pageZh({
  title: "买家小会：席位 / 对接 / 赞助合作（意向收集）",
  description: "面向中国企业：围绕展会的海外买家小会，席位、对接与赞助合作。活动未确认前仅收集意向。",
  canonical: `${D}/buyer-meetups/sponsorship/`,
  body: `
<h1>买家小会：席位、对接与赞助合作</h1>
<p>goChina Events 计划在展会期间举办小型商务交流：把<strong>品类清楚、经过筛选的海外买家</strong>与数量有限的匹配中国企业聚在一桌，洽谈在主展之外发生。</p>
<div class="notice"><p><strong>请先注意：</strong>当前没有已确认的活动日期、场地和到场名单。此页只收集合作意向与需求匹配；在真实买家出席得到确认前，我们不销售任何席位或赞助。席位价格在活动确认后按此页登记的匹配度单独报价。</p></div>
${sponsorshipFormZh()}
<script>${zhFormScript}</script>`,
}));

/* ------------------------------------------------------------ destinations */
fileWith("destinations/index.html", page({
  title: "Cities We Deliver In — Guangzhou, Foshan, Shanghai",
  description: "Where goChina Events can actually deliver: Guangzhou–Foshan and Shanghai today; other cities via verified partner arrangements only after confirmation.",
  canonical: `${D}/destinations/`,
  trail: [["goChina Events", "/"], ["Cities"]],
  body: `
<h1>Cities</h1>
<p>We publish a city only when transport, interpreting and supplier-visit coverage is real there. Today: <strong>Guangzhou–Foshan and Shanghai</strong>. For other cities we say plainly that services are partner-based and quoted per trip — instead of implying a permanent presence.</p>
${cards([
  { slug: "guangzhou", name: "Guangzhou & Foshan" },
  { slug: "shanghai", name: "Shanghai" },
], (c) => `<div class="card"><h3><a href="/destinations/${c.slug}/">${esc(c.name)}</a></h3><p>Transfers, interpreters, supplier visits.</p></div>`)}
${buyerForm({ compact: true, heading: "Enquiry" })}
${finalScript()}`,
}));

const CITY_PAGES = [
  {
    slug: "guangzhou",
    name: "Guangzhou & Foshan",
    body: `

<p class="lead">Canton Fair and CIFF live here; Foshan (Lecong) is China's densest furniture market. This is the core area we deliver in.</p>
<ul class="clean">${li([
  "Airport transfers, business vehicles, interpreters: available now.",
  "Supplier visit routes: Lecong showrooms, Dongguan factories, lighting and building materials districts.",
  "Fairs anchored here: <a href='/trade-shows/canton-fair/'>Canton Fair</a>, <a href='/trade-shows/ciff-guangzhou/'>CIFF Guangzhou</a>, <a href='/trade-shows/cips/'>CIPS</a>.",
])}</ul>`,
  },
  {
    slug: "shanghai",
    name: "Shanghai",
    body: `
<p class="lead">Shanghai anchors Yangtze Delta trips.</p>
<p class="lead">Yangtze Delta anchor: HOTELEX, CBE, Automechanika Shanghai, Intertextile — plus supplier towns reachable within one to two hours (Suzhou, Hangzhou, Ningbo).</p>
<ul class="clean">${li([
  "Show-day support, registration guidance: available now.",
  "Interpreters and vehicles: available now.",
  "Supplier visit routes: organized per industry, confirmed before the trip.",
])}</ul>`,
  },
];
for (const c of CITY_PAGES) {
  fileWith(`destinations/${c.slug}/index.html`, page({
    title: `${c.name} — Local Support Coverage`,
    description: `Local delivery coverage in ${c.name} for overseas trade show and sourcing visitors.`,
    canonical: `${D}/destinations/${c.slug}/`,
    trail: [["goChina Events", "/"], ["Cities", "/destinations/"], [c.name]],
    body: `<h1>${esc(c.name)}</h1>${c.body}
${buyerForm({ ctx: { show: c.name, source: `/destinations/${c.slug}/` }, compact: true })}
${finalScript()}`,
  }));
}

/* ---------------------------------------------------------------- guides */
fileWith("guides/index.html", page({
  title: "China Sourcing & Trade Show Guides — Decision-Type Articles",
  description: "Opinionated, practical guides for overseas buyers: Foshan furniture first visits, Canton Fair phases, interpreter vs sourcing agent, real costs of supplier-visit days.",
  canonical: `${D}/guides/`,
  trail: [["goChina Events", "/"], ["Guides"]],
  body: `
<h1>Guides</h1>
<p>Decision-type guides only. They're written to answer one question each so you can act — not to farm keyword variants.</p>
${cards(GUIDES, (g) => `<div class="card"><h3><a href="/guides/${g.slug}/">${esc(g.name)}</a></h3><p>${esc(g.summary)}</p></div>`)}
<p>Working documents, not just reading: see <a href="/templates/">sample files</a>.</p>`,
}));

for (const g of GUIDES) {
  fileWith(`guides/${g.slug}/index.html`, page({
    title: `${g.name} — goChina Events Guide`,
    description: g.summary,
    canonical: `${D}/guides/${g.slug}/`,
    trail: [["goChina Events", "/"], ["Guides", "/guides/"], [g.name]],
    extraJsonLd: [
      breadcrumbJsonLd([["Home", "/"], ["Guides", "/guides/"], [g.name, null]]),
      {
        "@context": "https://schema.org", "@type": "Article", headline: g.name,
        description: g.summary, author: { "@id": `${D}/#organization` },
        dateModified: new Date().toISOString().slice(0, 10),
      },
    ],
    body: `<h1>${esc(g.name)}</h1><p class="lead">${esc(g.summary)}</p>
${GUIDE_BODIES[g.slug] || ""}`,
  }));
}

/* ------------------------------------------- templates (sample documents) */
const TEMPLATE_CONTENT = {
  "sample-trip-plan": `
<h1>Sample Trip Plan</h1>
<div class="notice"><p><strong>This is a sample file</em> we show before booking, illustrating how trips are scoped. Real routes match your product list and confirmed supplier availability.</p></div>
<h2>Example: 3-day Guangzhou–Foshan furniture trip</h2>
<table>
<tr><th>Day</th><th>Plan</th><th>Delivery</th></tr>
<tr><td>Pre-trip</td><td>Requirement brief call; supplier shortlist (5–8); appointment confirmations</td><td>Brief note, shortlist, visit schedule</td></tr>
<tr><td>Day 1</td><td>2 showroom stops (Lecong main halls)</td><td>Meeting notes, spec sheets</td></tr>
<tr><td>Day 2</td><td>3 factory stops matched to your budget band</td><td>Same-evening notes: decisions & open items</td></tr>
<tr><td>Day 3</td><td>2 visits + sample / MOQ confirmations</td><td>Drill-down: quotes & follow-up plan</td></tr>
<tr><td>Post-trip</td><td>Comparison sheet; 2 follow-up rounds in agreed window</td><td>Comparison document</td></tr>
</table>`,
  "supplier-comparison": `
<h1>Supplier Comparison Template</h1>
<div class="notice"><p>All rows here are <strong>example values</strong> to show the format — never presented as validated suppliers.</p></div>
<table>
<tr><th>Field</th><th>Supplier A</th><th>Supplier B</th><th>Team notes</th></tr>
<tr><td>Product / spec</td><td>Armchair, PC frame, 350g vinyl</td><td>Armchair, metal frame, PU 380g</td><td>Fit our price band? Or above?</td></tr>
<tr><td>Price basis (qty)</td><td>$46 at 200 pcs</td><td>$49 at 100 pcs</td><td>Confirm what the price assumes</td></tr>
<tr><td>MOQ / mixed SKU</td><td>100, mixed OK</td><td>300, single color</td><td>How their rules fit our plan</td></tr>
<tr><td>Sample terms</td><td>2× price, refundable</td><td>Fixed fee, non-refundable</td><td>Cost per round of changes</td></tr>
<tr><td>Lead time</td><td>30 days</td><td>45 days</td><td>Affected by CNY weeks</td></tr>
<tr><td>Payment terms</td><td>30% down / 70% B&amp;L</td><td>50% / 50%</td><td>Read the down-payment terms carefully</td></tr>
<tr><td>Certification copies</td><td>on file</td><td>TO VERIFY</td><td>Never accept logos instead of docs</td></tr>
<tr><td>Open questions</td><td>–</td><td>Ask: spare parts after 12 months?</td><td>Every open item has an owner &amp; date</td></tr>
</table>`,
  "factory-visit-checklist": `
<h1>Factory Visit Checklist</h1>
<div class="notice"><p><strong>Sample</strong> — this is what we carry in a visit briefing; real checklists fit your product type and specs.</p></div>
<ul class="clean">${li([
  "<strong>Before:</strong> confirmed appointment date/time, contact person & mobile, host level (owner / sales / technical), parking note, visit length agreed.",
  "<strong>Capacity:</strong> production line running for our product family? Machines per line? Current utilization?",
  "<strong>Own shop vs outsourced:</strong> which stages of our product are done in-house vs subcontracted — see the workshops, not just offices.",
  "<strong>Sample / type-match:</strong> compare their displayed sample with our spec — exact material callouts; ask how finishes match across a production run.",
  "<strong>MOQ & lead time:</strong> per-SKU; lead time now (current loading includes CNY effects); impact of late test runs.",
  "<strong>QC:</strong> check the final QC station: what records are kept; how rejects are handled & reported.",
  "<strong>Packing:</strong> export packing standard, carton strength, mix-loading capability for less-than-full-container (LCL).",
  "<strong>After-visit step:</strong> who sends quotations by when; open questions recorded with an owner & dates in the meeting notes.",
])}</ul>`,
  "meeting-notes": `
<h1>Meeting Notes Template</h1>
<div class="notice"><p><strong>Sample</strong> of our same-evening meeting notes. Delivered after each accompanied meeting day when included in your package.</p></div>
<ul class="clean">${li([
  "<strong>Present:</strong> names, roles, contact level (owner / sales / technical).",
  "<strong>Confirmed by both sides:</strong> specifications & quantities discussed, prices and their assumptions, conditions in writing.",
  "<strong>Checked:</strong> samples, documents, certifications presented and recorded.",
  "<strong>Open items:</strong> every question pending, with the owner & promised date.",
  "<strong>Next steps:</strong> what each side will do next, by which date.",
])}</ul>`,
  "case-studies-index": `
<h1>Case studies</h1>
<div class="notice"><p><strong>Real client engagements are not published here yet.</strong> When a client authorizes publication of a real, completed trip, we publish it — with written permission and without inventing data. What you can evaluate meanwhile: the <a href="/templates/">sample files</a> our trips deliver and the honest <a href="/how-it-works/">process</a>.</p></div>`,
};

fileWith("templates/index.html", page({
  title: "Sample Documents — Trip Plan, Supplier Comparison, Visit Checklist, Meeting Notes",
  description: "Reusable sample files from how goChina Events works: sample trip plan, supplier comparison template, factory-visit checklist and meeting-notes template. Labeled samples, not client data.",
  canonical: `${D}/templates/`,
  trail: [["goChina Events", "/"], ["Sample documents"]],
  body: `
<h1>Sample documents</h1>
<p>Instead of unverifiable case studies, these are the working files a trip actually produces — <strong>all shown here as clearly labeled samples</strong> with example values, not client data.</p>
${cards(Object.entries(TEMPLATE_CONTENT).filter(([k]) => k !== "case-studies-index").map(([k]) => ({ slug: k })), (d) => {
  const t = TEMPLATE_CONTENT[d.slug].match(/<h1>(.*?)<\/h1>/)[1];
  return `<div class="card"><h3><a href="/templates/${d.slug}/">${esc(t)}</a></h3><p>Open as a page — copy what's useful.</p></div>`;
})}
`,
}));

for (const [slug, body] of Object.entries(TEMPLATE_CONTENT)) {
  if (slug === "case-studies-index") continue;
  fileWith(`templates/${slug}/index.html`, page({
    title: `${TEMPLATE_CONTENT[slug] ? TEMPLATE_CONTENT[slug].match(/<h1>(.*?)<\/h1>/)?.[1] : slug} — Sample`,
    description: "A labeled sample working document used on goChina Events trips.",
    canonical: `${D}/templates/${slug}/`,
    trail: [["goChina Events", "/"], ["Sample documents", "/templates/"], [body.match(/<h1>(.*?)<\/h1>/)[1]]],
    body: body,
  }));
}

/* ------------------------------------------------------------- trust pages */
fileWith("case-studies/index.html", page({
  title: "Case Studies — Published Only With Real Client Permission",
  description: "goChina Events publishes a case study only after a real, completed engagement with written client permission.",
  canonical: `${D}/case-studies/`,
  trail: [["goChina Events", "/"], ["Case studies"]],
  body: TEMPLATE_CONTENT["case-studies-index"],
}));

fileWith("how-it-works/index.html", page({
  title: "How It Works — Enquiry to Post-Trip Follow-Up",
  description: "The working process behind every goChina Events engagement: enquiry, planning call, quote, delivery in China, and documented follow-up.",
  canonical: `${D}/how-it-works/`,
  trail: [["goChina Events", "/"], ["How it works"]],
  body: `
<h1>How it works</h1>
<table>
<tr><th>Step</th><th>What happens</th><th>What you hold</th></tr>
<tr><td>1. Enquiry</td><td>You send what you have — incomplete is fine.</td><td>Reply within one business day.</td></tr>
<tr><td>2. Planning call</td><td>Dates, cities, categories, quantities, budget band; whether you need sourcing work or simply a support day.</td><td>Clear scope, on the record.</td></tr>
<tr><td>3. Quote & booking</td><td>Itemized quote: our fee(s) + pass-through costs. You confirm in writing.</td><td>Written scope, price & cancellation terms.</td></tr>
<tr><td>4. Pre-trip</td><td>Supplier shortlist, appointments, route & hotel options.</td><td>An itinerary you can still edit.</td></tr>
<tr><td>5. In China</td><td>Accompanied visits, interpreting, same-evening notes.</td><td>Structured records per meeting day.</td></tr>
<tr><td>6. Follow-up</td><td>Quote chasing, sample loops, third-party inspection & freight coordination.</td><td>Documented progress after you're home.</td></tr>
</table>
<h2>Who pays whom</h2>
<p>You pay <strong>us</strong> per the itemized quote. You pay <strong>supplier/hotel/freight parties directly</strong> unless a different arrangement is agreed in writing. Where a supplier-side fee may exist, it is disclosed up front; see <a href="/commercial-disclosure/">commercial disclosure</a>.</p>`,
}));

fileWith("pricing/index.html", page({
  title: "Pricing & Fees — How Quotes Are Built (Structure Examples, No Committed Amounts)",
  description: "How goChina Events quotes: fixed coordination fees, day rates, and third-party costs passed through at actual rates. Three non-committal trip budget examples with cost components.",
  canonical: `${D}/pricing/`,
  trail: [["goChina Events", "/"], ["Pricing & fees"]],
  body: `
<h1>Pricing & fees</h1>
<p>One price list can't be honest across industries and cities, so <strong>every engagement runs on an itemized written quote</strong>. What is always true:</p>
<table>
<tr><th>Type</th><th>How it works</th></tr>
<tr><td>Fixed coordination fee</td><td>Per trip/package, scoped on the planning call. Stated once in the quote.</td></tr>
<tr><td>Day rates</td><td>Interpreters and vehicles by day length, city and technical level; overtime stated upfront.</td></tr>
<tr><td>Per-piece work</td><td>Supplier research & shortlists by category and list depth.</td></tr>
<tr><td>Pass-through at actual</td><td>Hotels, transport, meals, third-party inspection, freight — separate lines at real provider rates, never silently marked up.</td></tr>
</table>
<h2>Three budget examples (structure, not committed prices)</h2>
${cards(PRICING_EXAMPLES, (e) => `
  <div class="card">
    <h3>${esc(e.name)}</h3>
    <p>${esc(e.who)}</p>
    <p><strong>Service components:</strong></p><ul class="clean" style="font-size:.9rem">${li(e.includes)}</ul>
    <p><strong>Pass-through (at actual cost):</strong></p><ul class="clean" style="font-size:.9rem">${li(e.passthroughs)}</ul>
    <p><strong>Cooperation income:</strong> ${esc(e.commissionNote)}</p>
    <p><strong>Not included:</strong> ${esc(e.outOfScope.join(" · "))}</p>
    <div class="meta" style="margin-top:10px">Amounts: published on the itemized quote once scope is agreed — current list prices not yet public.</div>
  </div>`)}
<h2>Payment & cancellation</h2>
<p>Written quotes state currency, payment schedule and cancellation terms — see <a href="/cancellations/">cancellations & refunds</a>. Enquiries never require payment or card details.</p>`,
}));

fileWith("supplier-selection/index.html", page({
  title: "How We Screen Suppliers — Method, Boundaries & Evidence",
  description: "The method behind a goChina Events shortlist: what is checked, when, with what evidence — and what stays with specialists, not us.",
  canonical: `${D}/supplier-selection/`,
  trail: [["goChina Events", "/"], ["How we screen suppliers"]],
  body: `
<h1>How we screen suppliers</h1>
<h2>Every shortlist entry carries an evidence note</h2>
<ul class="clean">${li([
  "What was checked — and <strong>when</strong> (a check from last year is stale and says so).",
  "What was confirmed vs what remains unverified — explicitly labeled.",
])}</ul>
<h2>The screening pass checks</h2>
<ul class="clean">${li([
  "<strong>Product fit:</strong> does the factory actually make your item, at your quantity, for your market?",
  "<strong>Own workshop vs trading layer:</strong> many intermediaries are fine — but you'll know which you're meeting.",
  "<strong>Willingness to host:</strong> some strong factories decline small/new orders; we confirm hosting before you fly, not at the gate.",
  "<strong>Contact level:</strong> a sales rep for a first visit is fine; for real orders you need a decision-capable contact.",
])}</ul>
<h2>What stays outside our judgment</h2>
<ul class="clean">${li([
  "Certification audits & quality verdicts — run by accredited inspectors (we coordinate, they certify).",
  "Deep engineering / legal questions — we arrange qualified specialists and say when a question exceeds our scope.",
])}</ul>
<h2>For suppliers: getting listed</h2>
<p>Chinese suppliers apply via the <a href="/partners/product-suppliers/">Chinese application page</a>. Every listed supplier keeps an evidence file; the page states what we verified and the date. We never present "verified" as our badge of honor — it's a documented record you can request at any time.</p>`,
}));

fileWith("commercial-disclosure/index.html", page({
  title: "Commercial Disclosure — Who Pays Us and How",
  description: "goChina Events income sources in plain language: client service fees, supplier-side cooperation income, local-service commissions — who pays, when it's disclosed, and how recommendations stay honest.",
  canonical: `${D}/commercial-disclosure/`,
  trail: [["goChina Events", "/"], ["Commercial disclosure"]],
  body: `
<h1>Commercial disclosure</h1>
<p>Three possible income sources, stated in one place:</p>
<table>
<tr><th>Income</th><th>Who pays</th><th>When you see it</th><th>Effect on recommendations</th></tr>
<tr><td>Client service fees</td><td>You — on the itemized quote</td><td>Before booking always</td><td>None: this is the work we bill</td></tr>
<tr><td>Supplier-side cooperation income</td><td>The supplier, if they have an agreement with us</td><td>In the quote & on relevant trip pages, before you confirm trips</td><td>We keep <strong>multiple candidates</strong> per category and say which, if any, are in such a relationship</td></tr>
<tr><td>Local service partner income</td><td>Vehicle/hotel/inspector partners, by contract</td><td>Disclosed where relevant, before the service</td><td>We present partner prices next to independent alternatives when these exist</td></tr>
</table>
<h2>Where the confusion normally lives</h2>
<p>"Third-party costs at actual rates" and "we may receive cooperation income" can collide if a partner pays us and their rate is shown unmarked. The rule: <strong>any partner-rate passed through shows an explicit line in the quote</strong>, so you can see which provider is a plain invoice and which is a contract partner.</p>
<h2>What we will not do</h2>
<ul class="clean">${li([
  "Present one supplier/recommendation as independent while hiding a paying relationship.",
  "Sell 'premium placement' in comparison tables.",
  "Invent testimonials, ratings or badges; paid relationships never masquerade as independent reviews.",
])}</ul>`,
}));

fileWith("about/index.html", page({
  title: "About goChina Events — Independent Buyer Support, Trial-Phase Transparency",
  description: "goChina Events is an independent China trip-planning & sourcing-support provider for overseas buyers. Early-stage service: verify everything on a call before money changes hands.",
  canonical: `${D}/about/`,
  trail: [["goChina Events", "/"], ["About"]],
  body: `
<h1>About</h1>
<p><strong>goChina Events</strong> is an independent China supply-chain development provider for overseas companies: supplier research & vetting, quote comparison, coordinated factory audits, sampling and order management — remote from day one, with on-the-ground support in Guangzhou-Foshan and Shanghai. We're a young service; we prove things one delivery at a time instead of claiming awards or headcounts we can't show.</p>
<h2>Service coverage</h2>
<table>
<tr><th>Item</th><th>Status</th></tr>
<tr><td>Cities — Guangzhou, Foshan, Shanghai</td><td>Live delivery today: transport, interpreters, supplier visits</td></tr>
<tr><td>Reviews / client list / certifications</td><td>Not published — no authorized client data exists yet</td></tr>
</table>
<h2>Legal identity & contacts — fields pending publication</h2>
<p>This service launches with separate domestic registrations and contact channels. Fields below go live the moment each item is confirmed; nothing here is invented in the meantime.</p>
<table>
<tr><th>Item</th><th>Status</th></tr>
<tr><td>Registered operating entity</td><td><em>To be confirmed and displayed here</em> — currently conversational service only, no contract powers claimed</td></tr>
<tr><td>Service email & WhatsApp</td><td><a href="mailto:${SITE.contact.email}">${SITE.contact.email}</a> · WhatsApp <a href="${SITE.contact.whatsappLink}" rel="noopener" target="_blank">${SITE.contact.whatsapp}</a></td></tr>
<tr><td>Working hours (CST)</td><td>${SITE.contact.hours}</td></tr>
</table>
<h2>Third-party services & their boundaries</h2>
<ul class="clean">${li([
  "Accredited inspection: coordinated through third-party inspectors; their reports & terms govern.",
  "Freight & customs: licensed forwarders; we coordinate the interface, not the liability.",
  "Machine/engineering judgment: qualified specialists on request.",
])}</ul>
${buyerForm({ compact: true, heading: "Enquiry" })}
${finalScript()}`,
}));

fileWith("contact/index.html", page({
  title: "Contact goChina Events",
  description: "Contact goChina Events: email contact@gochina.events, WhatsApp +86 182 2441 6343, or the enquiry form — answered within one business day.",
  canonical: `${D}/contact/`,
  trail: [["goChina Events", "/"], ["Contact"]],
  body: `
<h1>Contact</h1>
<table>
<tr><th>Channel</th><th>Detail</th></tr>
<tr><td>Enquiry (fastest)</td><td><a href="/plan-your-trip/">Plan My Trip form</a> — lands in our system, answered within one business day</td></tr>
<tr><td>Public email & WhatsApp</td><td><a href="mailto:${SITE.contact.email}">${SITE.contact.email}</a> · <a href="${SITE.contact.whatsappLink}" rel="noopener" target="_blank">WhatsApp ${SITE.contact.whatsapp}</a></td></tr>
<tr><td>Hours</td><td><strong>${SITE.contact.hours}</strong></td></tr>
<tr><td>In person</td><td>Guangzhou & Shanghai-area visits by appointment</td></tr>
<tr><td>China companies (中文)</td><td><a href="/partners/">合作伙伴入口</a></td></tr>
</table>
${buyerForm({ compact: true, heading: "Send an inquiry" })}
${finalScript()}`,
}));

fileWith("plan-your-trip/index.html", page({
  title: "Plan My Trip — Enquiry Form",
  description: "Tell us your China trip basics (name, contact, timing, industry/product and main need). We reply within one business day.",
  canonical: `${D}/plan-your-trip/`,
  trail: [["goChina Events", "/"], ["Plan My Trip"]],
  body: `<h1>Plan My Trip</h1>
<p>One form, one business day. Send what you have — most inquiries aren't fully decided yet, and that's exactly what the planning call exists for.</p>
${buyerForm({ heading: "Plan My Trip" })}
${finalScript()}`,
}));

fileWith("privacy/index.html", page({
  title: "Privacy",
  description: "How gochina.events handles enquiry data: collection, use, retention and your rights.",
  canonical: `${D}/privacy/`,
  trail: [["goChina Events", "/"], ["Privacy"]],
  body: `<h1>Privacy</h1>
<p>Enquiry form data (name, contact, message, page/UTM source) is used only to reply and to deliver a service you requested — not sold, not reused for unrelated campaigns. For arrangeable third parties (hotel, vehicle, inspector), only the minimum needed flows to them, and only after your confirmation.</p>
<h2>Retention & your rights</h2>
<p>Inquiry records are kept for our business records and audit; you can request a copy, correction or deletion — write from the address you used, via the <a href="/contact/">contact page</a>.</p>`,
}));

fileWith("terms/index.html", page({
  title: "Terms of Service",
  description: "goChina Events service terms: role, ordering and payment via itemized quotes, responsibilities, limitations.",
  canonical: `${D}/terms/`,
  trail: [["goChina Events", "/"], ["Terms"]],
  body: `<h1>Terms of Service</h1>
<p><strong>What we are.</strong> A coordination service: trip planning, interpreting, escorted visits, follow-up coordination. We are not an importer of record, not a party to between you-and-supplier sale contracts, and we don't guarantee orders or quality outcomes.</p>
<p><strong>Engagement model.</strong> Each trip/engagement runs on an itemized written quote (scope, inclusions/exclusions, currency, payment schedule, cancellation terms), which together with these general terms governs the work.</p>
<p><strong>Third-party terms.</strong> Hotels, transport, inspectors and forwarders carry their own conditions; we relay them to you before you confirm spending.</p>
<p><strong>Limitation.</strong> Liability limited to professional care of a local coordination service; nothing here replaces purchaser judgment or third-party certifications.</p>`,
}));

fileWith("cancellations/index.html", page({
  title: "Cancellations & Refunds",
  description: "goChina Events booking rules: fixed-fee refund schedule vs third-party pass-through costs when plans change.",
  canonical: `${D}/cancellations/`,
  trail: [["goChina Events", "/"], ["Cancellations"]],
  body: `<h1>Cancellations & refunds</h1>
<ul class="clean">${li([
  "<strong>Our coordination fees:</strong> refundable per the schedule on your quote — typically full refund before pre-trip work starts, reduced once appointments are made, fast-cancel terms where a fair date shifts the plan.",
  "<strong>Third-party costs</strong> (hotel, vehicle, inspection, freight): governed by those providers' own rules; we show their cutoffs before you confirm, and refund what they refund.",
  "<strong>Date changes:</strong> rescheduling within the same fair window is usually free; provider-side change fees are billed at actual.",
])}</ul>
<p>Sample schedules ship on request with every written quote before payment.</p>`,
}));

/* ------------------------------------------------------------- file 404 */
fileWith("404.html", page({
  title: "404 — Page Not Found | goChina Events",
  description: "Page not found. Start from the homepage or send an inquiry.",
  canonical: `${D}/404`,
  showCrumbs: false,
  body: `<h1>Page not found</h1>
<p>The old site was retired; some of its URLs have no direct successor. Useful starting points:</p>
<ul class="clean">${li([
  "<a href='/'>Homepage</a>",
  "<a href='/trade-shows/'>Trade shows</a> · <a href='/industries/'>Industries</a> · <a href='/services/'>Services</a>",
  "<a href='/plan-your-trip/'>Plan My Trip</a> — tell us what you were trying to do; we'll point you to it.",
])}</ul>`,
}));

/* ------------------------------------------------- partners (unchanged zh) */
fileWith("partners/index.html", pageZh({
  title: "合作入口（中文）— 供应商 / 服务商 / 赞助合作",
  description: "与 goChina Events 合作：中国产品供应商合作、本地服务商（酒店、车队、翻译、验货、货代）合作、买家小会赞助意向收集。",
  canonical: `${D}/partners/`,
  body: `
<h1>与 goChina Events 合作</h1>
<p>我们服务来华参展与采购的海外买家，为国内工厂、出口企业与本地服务商带来<strong>身份明确、需求真实的客户</strong>。合作细节（客户归属、计佣范围、结算节点）<strong>逐家书面确认</strong>，不在网站上公布统一佣金数字。</p>
${cards([
  { href: "/partners/product-suppliers/", h: "产品供应商合作", d: "工厂、贸易公司、展厅：客户引荐与合作规则说明。" },
  { href: "/partners/local-services/", h: "本地服务商合作", d: "酒店、车队、商务翻译、第三方验货、货代物流。" },
  { href: "/buyer-meetups/sponsorship/", h: "买家小会赞助/参会", d: "席位、对接与赞助合作的意向收集（活动确认前不售票）。" },
], (c) => `<div class="card"><h3><a href="${c.href}">${esc(c.h)}</a></h3><p>${esc(c.d)}</p></div>`)}
`,
}));
fileWith("partners/product-suppliers/index.html", pageZh({
  title: "产品供应商合作申请（中文）",
  description: "工厂与贸易公司合作申请：客户引荐、归属与佣金结算说明。",
  canonical: `${D}/partners/product-suppliers/`,
  body: `<h1>产品供应商合作</h1>${supplierFormZh()}<script>${zhFormScript}</script>`,
}));
fileWith("partners/local-services/index.html", pageZh({
  title: "本地服务商合作申请（中文）",
  description: "酒店、车队、商务翻译、验货机构、货代物流合作申请。",
  canonical: `${D}/partners/local-services/`,
  body: `<h1>本地服务商合作</h1>${localServiceFormZh()}<script>${zhFormScript}</script>`,
}));

/* --------------------------------------------------------- photo credits */
fileWith("photo-credits/index.html", page({
  title: "Photo Credits — Licensing & Sources (Wikimedia Commons)",
  description: "Attribution and license information for the photos used on gochina.events.",
  canonical: `${D}/photo-credits/`,
  trail: [["goChina Events", "/"], ["Photo credits"]],
  body: `
<h1>Photo credits</h1>
<p>Our own on-site photography (factory visits, showrooms, vehicles, meetings) will replace these as active work proceeds; until then the scene photos below are licensed with attribution, per their terms:</p>
<table>
<tr><th>Photo</th><th>Author</th><th>License</th><th>Source</th></tr>
${PHOTOS.map((p) => `<tr><td>${esc(p.caption)}</td><td>${esc(p.artist)}</td><td>${esc(p.license)}</td><td><a href="${esc(p.source)}" rel="noopener" target="_blank">Wikimedia Commons</a></td></tr>`).join("")}
</table>`,
}));

/* ----------------------------------------------------------------- blog */
const published = () => POSTS.filter((p) => p.status === "published");

/* ---------------------------------------------- feed.xml (AI/RSS pickup) */
fileWith("feed.xml", `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>goChina Events — China sourcing blog</title>
<link>${D}/blog/</link>
<atom:link href="${D}/feed.xml" rel="self" type="application/rss+xml"/>
<description>One real sourcing question answered daily: quotes, sampling, freight, factory tiers, market routes for overseas buyers in China.</description>
<language>en</language>
${published().slice(0, 20).map((p) => `
<item>
<title>${esc(p.title)}</title>
<link>${D}/blog/${p.slug}/</link>
<guid>${D}/blog/${p.slug}/</guid>
<pubDate>${new Date(p.date).toUTCString()}</pubDate>
<description>${esc(p.summary)}</description>
</item>`).join("")}
</channel>
</rss>`);

fileWith("blog/index.html", page({
  title: "China Sourcing Blog — One Honest Question Answered Daily",
  description: "Daily decision-type posts for overseas buyers in China: reading quotes, sampling, freight, factory tiers, market routes. No keyword-farm posts.",
  canonical: `${D}/blog/`,
  trail: [["goChina Events", "/"], ["Blog"]],
  body: `
<h1>Blog — one real sourcing question, answered daily</h1>
<p>Straight answers to practical questions, one topic at a time. Long structure lives in <a href="/guides/">Guides</a>; this is the running notebook.</p>
${cards(published(), (p) => `
  <div class="card"><h3><a href="/blog/${p.slug}/">${esc(p.title)}</a></h3><p>${esc(p.summary)}</p>
  <div class="meta">${esc(p.date)}</div></div>`)}
<p class="meta" style="color:#8a97a3">Next topics are on the editorial board — one real question per day, no filler.</p>`,
}));
for (const p of published()) {
  fileWith(`blog/${p.slug}/index.html`, page({
    title: `${p.title} — goChina Events Blog`,
    description: p.summary,
    canonical: `${D}/blog/${p.slug}/`,
    trail: [["goChina Events", "/"], ["Blog", "/blog/"], [p.title]],
    extraJsonLd: [
      breadcrumbJsonLd([["Home", "/"], ["Blog", "/blog/"], [p.title, null]]),
      {
        "@context": "https://schema.org", "@type": "BlogPosting", headline: p.title,
        description: p.summary, datePublished: p.date, dateModified: p.date,
        author: { "@id": `${D}/#organization` },
        mainEntityOfPage: `${D}/blog/${p.slug}/`,
      },
    ],
    body: `<h1>${esc(p.title)}</h1>
<p class="meta" style="color:#8a97a3">Published ${esc(p.date)} · goChina Events editorial</p>
${p.body || ""}
<p>Related question? <a href="/plan-your-trip/">Ask us</a> · <a href="/blog/">Blog</a> · <a href="/guides/">Guides</a></p>`,
  }));
}

/* robots etc */
fileWith("robots.txt", `User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Bytespider
Allow: /

User-agent: Applebot
Allow: /

User-agent: *
Allow: /

Sitemap: ${D}/sitemap.xml
`);

fileWith("llms.txt", `# goChina Events
goChina Events is an independent China supply-chain development provider for overseas companies: supplier research & vetting, quote comparison, coordinated factory audits, sampling and order milestone management — remote from day one, plus on-the-ground support in Guangzhou-Foshan and Shanghai. Trade show trip support is offered as an entry service. Not affiliated with any trade fair organizer; supplier/partner relationships disclosed at ${D}/commercial-disclosure/.

## Pages
- [Home](${D}/): overview of remote supply-chain development and China visit services.
- [Trade Shows](${D}/trade-shows/): supported entry channel; verified dates where published, official organizer links.
- [Industries](${D}/industries/): eight sourcing industries with MOQs, screening points, clusters and visit notes.
- [Services](${D}/services/): supplier research & vetting, purchasing & order coordination, inspection & freight coordination, factory visits, interpreters, show support, transfers.
- [Business Trips](${D}/business-trips/): supported visit structures.
- [Pricing](${D}/pricing/): fee structure + labeled budget examples (no committed amounts).
- [Commercial disclosure](${D}/commercial-disclosure/)
- [How we screen suppliers](${D}/supplier-selection/)
- [Sample documents](${D}/templates/): trip plan, comparison sheet, visit checklist, meeting notes.
- [Buyer Meetups](${D}/buyer-meetups/): interest list; no confirmed events published.
- [Blog](${D}/blog/): one sourcing question answered daily; machine-readable feed at ${D}/feed.xml (RSS).
- [Plan a project](${D}/plan-your-trip/): enquiry form; response within one business day.

Contact: email ${SITE.contact.email}, WhatsApp ${SITE.contact.whatsapp}, hours ${SITE.contact.hours}.
`);;
fileWith("og.png", readFileSync(`${ROOT}src/og.png`));
for (const keyFile of ["2f04070786fc7fabc5c5b689d553901e.txt"]) {
  fileWith(keyFile, readFileSync(`${ROOT}src/${keyFile}`));
}
for (const p of PHOTOS) {
  fileWith(`img/${p.file.split("/")[2]}`, readFileSync(`${ROOT}src/img/${p.file.split("/").pop()}`));
}
fileWith("favicon.ico", readFileSync(`${ROOT}src/favicon.ico`));
fileWith("BingSiteAuth.xml", readFileSync(`${ROOT}src/BingSiteAuth.xml`));

/* ----------------------------------------------------------------- sitemap */
const today = new Date().toISOString().slice(0, 10);
const all = [
  ["/"],
  ["/trade-shows/"], ["/industries/"], ["/services/"], ["/business-trips/"],
  ["/buyer-meetups/"], ["/buyer-meetups/sponsorship/"], ["/destinations/"],
  ...TRADE_SHOWS.map((s) => [`/trade-shows/${s.slug}/`]),
  ...INDUSTRIES.map((i) => [`/industries/${i.slug}/`]),
  ...SVC_ORDER.map((slug) => [`/services/${slug}/`]),
  ...TRIPS.map((t) => [`/business-trips/${t.slug}/`]),
  ...GUIDES.map((g) => [`/guides/${g.slug}/`]),
  ["/blog/"],
  ...POSTS.filter((p) => p.status === "published").map((p) => [`/blog/${p.slug}/`]),
  ["/templates/"], ["/templates/sample-trip-plan/"], ["/templates/supplier-comparison/"],
  ["/templates/factory-visit-checklist/"], ["/templates/meeting-notes/"],
  ["/destinations/guangzhou/"], ["/destinations/shanghai/"],
  ["/how-it-works/"], ["/pricing/"], ["/supplier-selection/"], ["/commercial-disclosure/"],
  ["/about/"], ["/contact/"], ["/case-studies/"], ["/photo-credits/"],
  ["/partners/"], ["/partners/product-suppliers/"], ["/partners/local-services/"],
  ["/privacy/"], ["/terms/"], ["/cancellations/"], ["/plan-your-trip/"],
];
fileWith("sitemap.xml", `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${all.map(([u]) => `  <url><loc>${D}${u}</loc><lastmod>${today}</lastmod></url>`).join("\n")}
</urlset>`);

console.log("Build OK —", all.length, "pages in sitemap");
