// Shared layout helpers for the gochina.events build.
import { SITE, FOOTER_COLS } from "../src/content.mjs";

export const esc = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export const organizationJsonLd = () => ({
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": `${SITE.domain}/#organization`,
  name: SITE.name,
  url: SITE.domain,
  description: SITE.description,
  logo: `${SITE.domain}/og.png`,
  email: SITE.contact && SITE.contact.email ? `mailto:${SITE.contact.email}` : undefined,
  ...(SITE.contact
    ? {
        contactPoint: [
          {
            "@type": "ContactPoint",
            contactType: "customer service",
            email: SITE.contact.email,
            telephone: SITE.contact.whatsapp.replace(/\s/g, ""),
            availableLanguage: ["en", "zh"],
            hoursAvailable: "Mo-Su 08:30-19:00",
          },
        ],
      }
    : {}),
});

export const breadcrumbJsonLd = (trail) => ({
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: trail.map(([name, url], i) => ({
    "@type": "ListItem", position: i + 1, name,
    ...(url ? { item: url } : {}),
  })),
});

export const serviceJsonLd = ({ name, description, url, serviceType }) => ({
  "@context": "https://schema.org",
  "@type": "Service",
  serviceType,
  name,
  description,
  url,
  provider: { "@id": `${SITE.domain}/#organization` },
});

const navScript = `
(function(){
  var t=document.querySelector('.nav-toggle');
  if(!t)return;
  t.addEventListener('click',function(){
    var open=t.getAttribute('aria-expanded')==='true';
    t.setAttribute('aria-expanded',open?'false':'true');
    document.body.classList.toggle('nav-open',!open);
  });
})();`;

const REAL_NAV = [
  { href: "/trade-shows/", label: "Trade Shows" },
  { href: "/industries/", label: "Industries" },
  { href: "/services/", label: "Services" },
  { href: "/business-trips/", label: "Business Trips" },
  { href: "/buyer-meetups/", label: "Buyer Meetups" },
];

const REAL_FOOTER = [
  {
    title: "Plan",
    links: [
      { href: "/plan-your-trip/", label: "Plan My Trip (inquiry)" },
      { href: "/how-it-works/", label: "How it works" },
      { href: "/pricing/", label: "Pricing & fees" },
      { href: "/destinations/", label: "Cities" },
      { href: "/guides/", label: "Guides" },
      { href: "/templates/", label: "Sample documents" },
    ],
  },
  {
    title: "Trust",
    links: [
      { href: "/supplier-selection/", label: "How we screen suppliers" },
      { href: "/commercial-disclosure/", label: "Commercial disclosure" },
      { href: "/about/", label: "About & preview" },
      { href: "/contact/", label: "Contact" },
    ],
  },
  {
    title: "China partners (中文)",
    links: [
      { href: "/partners/", label: "合作伙伴入口" },
      { href: "/partners/product-suppliers/", label: "产品供应商合作" },
      { href: "/partners/local-services/", label: "本地服务商合作" },
      { href: "/buyer-meetups/sponsorship/", label: "买家小会赞助合作" },
    ],
  },
  {
    title: "Policies",
    links: [
      { href: "/privacy/", label: "Privacy" },
      { href: "/terms/", label: "Terms of service" },
      { href: "/cancellations/", label: "Cancellations & refunds" },
    ],
  },
];

export const caseStudiesLink = { href: "/case-studies/", label: "Case studies" };

/**
 * Page shell (English).
 */
export function page({ title, description, canonical, body, trail = [], extraJsonLd = [], showCrumbs = true }) {
  const crumbs =
    showCrumbs && trail.length > 1
      ? `<nav class="crumbs" aria-label="Breadcrumb">${trail
          .map(([t, h], i) => (i === trail.length - 1 ? `<span aria-current="page">${esc(t)}</span>` : `<a href="${h}">${esc(t)}</a> <span class="sep">/</span>`))
          .join(" ")}</nav>`
      : "";
  const nav = REAL_NAV.map((n) => `<a href="${n.href}">${esc(n.label)}</a>`).join("");
  const foot = FOOTER_COLS.map(
    (c) => `<div class="fcol"><h4>${esc(c.title)}</h4>${c.links.map((l) => `<a href="${l.href}">${esc(l.label)}</a>`).join("")}</div>`
  ).join("");
  const ld = [...extraJsonLd, organizationJsonLd()];

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${esc(canonical)}">
<link rel="alternate" hreflang="en" href="${esc(canonical)}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="stylesheet" href="/styles.css">
<meta property="og:type" content="website">
<meta property="og:site_name" content="goChina Events">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${esc(canonical)}">
<meta property="og:image" content="${SITE.domain}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(description)}">
<meta name="twitter:image" content="${SITE.domain}/og.png">
${ld.map((j) => `<script type="application/ld+json">${JSON.stringify(j)}</script>`).join("\n")}
</head>
<body>
<header class="site-head">
  <div class="wrap head-in">
    <a class="brand" href="/">goChina<span>Events</span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="mainnav" aria-label="Open menu">Menu</button>
    <nav class="mainnav" id="mainnav" aria-label="Main">${nav}<a class="cta ghost" href="${SITE.contact.whatsappLink}" rel="noopener" target="_blank">WhatsApp</a><a class="cta" href="/plan-your-trip/">Plan My Trip</a></nav>
  </div>
</header>
<a class="wa-float" href="${SITE.contact.whatsappLink}" rel="noopener" target="_blank" aria-label="Chat on WhatsApp">WhatsApp</a>
<div class="wrap crumbs-wrap">${crumbs}</div>
<main class="wrap">
${body}
</main>
<footer class="site-foot">
  <div class="wrap foot-in">
    ${foot}
  </div>
  <div class="wrap foot-legal">
    <p><strong>Contact:</strong> <a href="mailto:${SITE.contact.email}">${SITE.contact.email}</a> · WhatsApp <a href="${SITE.contact.whatsappLink}" rel="noopener" target="_blank">${SITE.contact.whatsapp}</a> · ${SITE.contact.hours}</p>
    <p>goChina Events is an independent China supply-chain development provider for overseas companies: supplier research & vetting, quote comparison, coordinated factory audits, sampling and order management — remote from day one, with on-the-ground support in Guangzhou-Foshan and Shanghai. Trade show trip support is one of our entry services, not our core business. Commercial relationships with suppliers are disclosed on <a href="/commercial-disclosure/">our disclosure page</a>.</p>
    <p class="trial">© ${new Date().getFullYear()} goChina Events · new-service preview: we reply to every enquiry, and you can verify us on one scheduled call before paying anything.</p>
  </div>
</footer>
<script>${navScript}</script>
<script>
fetch('/api/track',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
p:location.pathname,r:document.referrer.slice(0,200),l:navigator.language.slice(0,10),w:window.innerWidth
})});
</script>
</body>
</html>`;
}

/* Chinese partner-facing shell */
export function pageZh({ title, description, canonical, body }) {
  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${esc(canonical)}">
<link rel="stylesheet" href="/styles.css">
<meta property="og:image" content="${SITE.domain}/og.png">
</head>
<body>
<header class="site-head">
  <div class="wrap head-in">
    <a class="brand" href="/">goChina<span>Events</span></a>
    <nav class="mainnav"><a href="/">English site</a><a href="/partners/">合作入口</a></nav>
  </div>
</header>
<main class="wrap zh">
${body}
</main>
<footer class="site-foot"><div class="wrap foot-legal">
<p>goChina Events 是独立商务接待与采购协调服务商，非任何第三方展会的主办方或官方售票机构。商务合作关系见 <a href="/commercial-disclosure/">披露页</a>。</p>
</div></footer>
</body>
</html>`;
}

export const li = (items) => items.map((t) => `<li>${t}</li>`).join("");
export const cards = (arr, fn) => `<div class="cards">${arr.map(fn).join("")}</div>`;
