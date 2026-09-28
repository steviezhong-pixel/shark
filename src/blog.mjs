// blog.mjs — editorial board. Each entry = one decision-type post.
// 铁律：只写回答真实买家问题的文章；日更但每篇必须有独立知识点，无话题重复填充。
// 状态: published (正常板块) / idea (排队中/未写)

export const POSTS = [
  {
    slug: "how-to-read-a-chinese-supplier-quote",
    title: "How to read a Chinese supplier quote — and what's usually missing",
    summary: "Six line items a real quote should contain, the two questions that catch 80% of confusion, and how to compare quotes you received years apart.",
    date: "2026-09-20",
    status: "published",
    body: `
<p>A "quote" from the right supplier answers a decision. A bad quote opens a negotiation that never ends. Here's what a usable quote contains — and what its absence means.</p>
<h3>The six things a complete quote states</h3>
<table>
<tr><th>Item</th><th>Why it matters</th></tr>
<tr><td>Price basis (quantity + specs + options)</td><td>"$18.50" means nothing. $18.50 at 500 pcs, kraft box, matte finish — now it can be compared.</td></tr>
<tr><td>Inclusions and exclusions</td><td>Packaging, printing, tooling fees, testing, freight terms (FOB/CIF/EXW) all hide here.</td></tr>
<tr><td>Lead time and current loading</td><td>A 30-day lead time in a loaded factory is not the same as one in a slow month.</td></tr>
<tr><td>Payment terms</td><td>30/70 against B&amp;L is standard; 50/50 upfront on a new client usually signals cash pressure.</td></tr>
<tr><td>Sample policy</td><td>Who pays, is it creditable, how many rounds are included.</td></tr>
<tr><td>What needs confirmation</td><td>An honest quote lists open items. A "perfect" quote with zero open items is the one to re-check.</td></tr>
</table>
<h3>The two questions that clarify half the confusion</h3>
<ul class="clean">
<li>"Is this price at MOQ, at my quantity, or at your preferred quantity?" — most mispriced orders fail here.</li>
<li>"If I change the quantity later, what happens to the unit price?" — reveals whether the price is a real ladder or a bait number.</li>
</ul>
<h3>Comparing quotes across suppliers</h3>
<p>Normalizing quotes is what our <a href="/templates/supplier-comparison/">comparison template</a> exists for: same fields, per supplier, with each open question assigned an owner and date. Quotes that arrive years apart should also be re-basesed against the same raw material indices — steel, resin, freight.</p>
<p>Not sure whether a quote you received is complete? Send it to us in an <a href="/plan-your-trip/">enquiry</a> — we'll tell you what's missing, no charge, no obligation.</p>`,
  },
  {
    slug: "guangzhou-vs-yiwu-where-to-source",
    title: "Guangzhou vs Yiwu: which market should your first China sourcing trip visit?",
    summary: "Category fit, order sizes, and how a first trip is usually split between the two — with honest tradeoffs.",
    date: "2026-09-20",
    status: "published",
    body: `<p>If you are visiting China for the first time to source products, the choice between Guangzhou and Yiwu is really a question about what you are buying and in what volume — not which city is "better." They serve fundamentally different purposes.</p>
<h3>The core difference in one line</h3>
<p>Guangzhou is a <strong>manufacturing and trade fair hub</strong> — you go there to meet factories, attend industry exhibitions, and negotiate production deals across broad categories. Yiwu is a <strong>wholesale market</strong> — you go there to browse a dense concentration of small-lot merchandise from many suppliers under one roof.</p>
<h3>When Guangzhou makes more sense</h3>
<ul class="clean">
<li>Your product falls into furniture, building materials, lighting, hardware, automotive parts, textiles, or electronics — categories with deep factory ecosystems clustered in the Pearl River Delta.</li>
<li>Your intended order size is meaningful: MOQs commonly start at several hundred to a few thousand units, and lead times typically run 30–60 days after sampling.</li>
<li>You want to attend a trade fair during your visit. Canton Fair and CIFF draw verified international buyers and supplier pavilions several times a year.</li>
<li>You expect to visit factories in person — the city's logistics and supplier density make multi-day factory routes practical.</li>
</ul>
<h3>When Yiwu makes more sense</h3>
<ul class="clean">
<li>You are sourcing small commodities: accessories, household goods, stationery, toys, small electronics, or seasonal items sold in low minimums.</li>
<li>Your order quantities are small or you want to test a product concept before committing to production volumes.</li>
<li>You need to compare many suppliers quickly — the market's structure lets you visit dozens of stalls in a single day.</li>
<li>You are buying finished goods rather than having something manufactured to your specification.</li>
</ul>
<h3>How a first trip is usually split</h3>
<p>A common pattern: buyers focused on manufacturing categories spend most of their time in Guangzhou, often combining it with nearby Foshan for furniture or Dongguan for electronics and hardware. Buyers whose needs span small commodities and manufactured goods sometimes split a longer trip between both cities — typically two to three days at the Yiwu market followed by factory visits in the Guangzhou area.</p>
<h3>What to watch for</h3>
<ul class="clean">
<li>In Guangzhou, supplier meetings are appointment-driven. Confirm visits in advance; walk-in access to factory floors is rarely guaranteed.</li>
<li>In Yiwu, the market is open to browsers, but serious pricing conversations still require a local contact or interpreter — many vendors focus on domestic buyers during peak periods.</li>
<li>Neither city guarantees a single "best" supplier. The realistic approach is to build a shortlist of two to three candidates per category and compare.</li>
</ul>
<p>Not sure which city fits your product category and order size? <a href="/industries/">Check the industry pages</a> for a sense of where your product sits, then <a href="/plan-your-trip/">plan your trip</a> — we can help you build a route that matches your category, quantities, and timeline.</p>`,
  },
  {
    slug: "reading-supplier-factory-tier-signals",
    title: "Reading factory tier signals: what the office lobby, the sample room and the loading bay tell you",
    summary: "On-site evidence you can check in a 20-minute walk-through — before trusting any claim sheet.",
    date: "2026-09-20",
    status: "published",
    body: `<p>A factory's tier is visible within twenty minutes of walking in — if you know what to look at and don't stop at the reception desk. Here's what the lobby, the sample room, and the loading bay actually reveal, and why each area tells a different part of the story.</p>
<h3>The office lobby</h3>
<p>What you see in the lobby sets expectations before a single conversation starts, and experienced buyers know this is where the first impressions are earned or lost.</p>
<ul class="clean">
<li><strong>Signage and branding consistency.</strong> A lobby with a dated banner, mismatched fonts, or peeling wall panels usually means the company's internal standards haven't been reviewed in years — not that they're deliberately sloppy.</li>
<li><strong>Meeting setup.</strong> A dedicated conference room with a whiteboard, printed agendas, and water signals an operation that runs structured meetings. A "conference area" that doubles as a storage room suggests ad-hoc processes.</li>
<li><strong>Language capability.</strong> Having at least one English-speaking contact ready, versus relying on a phone translation app, tells you whether they handle international orders routinely or are still building toward that market.</li>
<li><strong>Documentation on display.</strong> Certificates or quality charts posted visibly suggest they value their compliance record. Their absence doesn't mean there are none — it means you should ask.</li>
</ul>
<h3>The sample room</h3>
<p>This is where tier claims get tested against reality, and the gap between presentation and substance is often widest here.</p>
<table>
<tr><th>Signal</th><th>What it likely means</th></tr>
<tr><td>Samples are current and labeled</td><td>They produce to market specs now, not from an old catalog.</td></tr>
<tr><td>Physical samples available to touch</td><td>They make the real thing — not just resell third-party goods under their name.</td></tr>
<tr><td>Sample room shows one or two product families only</td><td>Depth, not breadth; could be a focused specialist or a narrow production line.</td></tr>
<tr><td>Samples are pristine but the factory floor looks different</td><td>The display room is set up for visits; the production line tells the real story.</td></tr>
</table>
<p>A common pattern in the mid-tier range: the sample room is polished and the visitor walks away impressed — until the production area shows different tolerances and materials. The reverse is also true and is worth noting.</p>
<h3>The loading bay</h3>
<p>The loading bay is the least decorated and most honest part of a factory, because it's where the work gets shipped.</p>
<ul class="clean">
<li><strong>Carton marking.</strong> Consistently marked cartons with product codes, destination ports, and quantities suggest routine export work. Loose or handwritten labels suggest ad-hoc orders or a newer exporter.</li>
<li><strong>Loading pace.</strong> A crew working with a plan — pallets numbered, forklift drivers on a schedule — indicates regular shipping volumes. Idle forklifts with no queue suggest sporadic orders.</li>
<li><strong>Mixed freight.</strong> Seeing LCL (less-than-container) shipments mixed with full containers suggests they serve both small and large buyers, which is common across typical tiers.</li>
</ul>
<h3>Putting it together</h3>
<p>No single signal is decisive on its own. A polished lobby with a disorganized loading bay, or a well-stocked sample room with nothing on the factory floor, are both worth asking follow-up questions about. The tiers are not a ladder of "good" and "bad" — they reflect focus, export experience, and operational maturity, and they match different buyer needs. Some buyers need a focused specialist; others need a broad-line supplier with mixed-tier flexibility.</p>
<p>See our <a href="/industries/">industry pages</a> for a sense of what each product category tends to reveal on a factory floor.</p>
<p>Ready to see these signals for yourself? <a href="/plan-your-trip/">Plan your trip</a> — we'll walk the route with you and point out what each area reveals.</p>`,
  },
  {
    slug: "hotel-furniture-project-buying-in-china",
    title: "Buying furniture for a small hotel project in China: rooms, rates and realistic lead times",
    summary: "A project-based sourcing tour: which suppliers, what approval chains, why 'one / same factory' rarely happens.",
    date: "2026-09-20", status: "published",
body: `<p>If you are buying furniture for a small hotel in China, the real question is not whether you can find a factory — it is which type of supplier matches your project scope, approval chain, and timeline. Most first-time hotel buyers discover that treating furniture sourcing like a single-product order leads to delays, misaligned specifications, and budget overruns that were avoidable with the right supplier structure.</p>
<h3>What you are actually buying</h3>
<p>Hotel furniture projects typically span guest room suites, lobby and common-area seating, conference or meeting room sets, and restaurant or bar furnishings. Each category may come from a different supplier, because factories tend to specialise in a narrow product range. A bedroom furniture line rarely overlaps with the workshop that produces lobby sofas, and expecting one factory to cover the full scope usually means accepting compromises on quality or lead time.</p>
<p>Understanding this split early helps you set realistic expectations. You are not placing a single order — you are coordinating a multi-category project with its own approval chain, sampling timeline, and delivery logistics. Treating it as one purchase rather than several related projects is the most common mistake first-time buyers make.</p>
<h3>Typical supplier types for hotel projects</h3>
<table>
<tr><th>Supplier type</th><th>Best for</th><th>Typical lead time</th></tr>
<tr><td>Dedicated hotel furniture factory</td><td>Full-room suites with consistent finish and matching hardware</td><td>45–75 days after sample approval</td></tr>
<tr><td>Regional woodworking factory</td><td>Custom pieces, locally sourced timber, or smaller MOQs</td><td>30–60 days; varies with order complexity</td></tr>
<tr><td>Trading company</td><td>Coordinating multiple categories under one contract</td><td>Adds 1–2 weeks; simplifies administrative workload</td></tr>
<tr><td>OEM/ODM manufacturer</td><td>Branded or designed-to-specification pieces requiring custom tooling</td><td>60–90 days including tooling and sample iterations</td></tr>
</table>
<h3>The approval chain you need to plan for</h3>
<p>Hotel projects almost always require sign-off from more than one person before production starts. The interior designer specifies finishes, the procurement team negotiates terms, and the property owner or brand standards team approves samples. A common pattern is two to three rounds of sample approval, each taking one to two weeks depending on how quickly feedback loops back.</p>
<ul class="clean">
<li><strong>Material confirmation.</strong> Wood species, veneer type, fabric grade, and finish colour all need sign-off before cutting begins.</li>
<li><strong>Sample room review.</strong> Most buyers request one complete room set as a reference. Expect to review, revise, and re-submit at least once.</li>
<li><strong>Brand standards compliance.</strong> Hardware finishes, label placement, and packaging may need to match brand guidelines precisely.</li>
<li><strong>Lead time agreement.</strong> Confirm whether the quoted timeline includes sampling, tooling, or production only.</li>
</ul>
<h3>Lead times and realistic scheduling</h3>
<p>Project timelines commonly run 60–120 days from sample approval to delivery, depending on room count and customization level. Sampling rounds add two to four weeks to the schedule. Planning a sourcing trip four to six weeks before you need samples approved gives enough buffer to inspect the factory floor and make decisions on-site.</p>
<h3>What to verify before committing</h3>
<ul class="clean">
<li>Whether the factory has completed hotel projects before and what types of properties they have supplied</li>
<li>Whether they can produce the full range of pieces or will subcontract part of the scope</li>
<li>How they handle on-site installation or whether a separate fit-out team is required</li>
<li>What their warranty terms cover for structural elements versus upholstery and soft goods</li>
<li>Whether they have the capacity to absorb your order alongside existing commitments</li>
</ul>
<p>For a deeper look at what to expect on a furniture sourcing trip, see our <a href="/guides/foshan-furniture-first-visit/">guide to visiting furniture factories</a>.</p>
<p>Not sure how your project scope maps to the right supplier type and timeline? <a href="/plan-your-trip/">Plan your trip</a> and we can help you build a sourcing route that matches your categories, approval timeline, and budget.</p>`,
  },
  {
    slug: "packing-and-lcl-vs-fcl-vs-air",
    summary: "When a mixed sea container beats LCL and Air on true landed cost — with the paperwork flags.",
    title: "LCL vs FCL vs air freight from China: what actually changes the landed price",
    date: null, status: "idea",
  },
  {
    slug: "first-inquiry-to-supplier-emails",
    title: "Your first supplier emails: what to ask to sound like someone worth quoting",
    summary: "The seven-line message that gets quoted in 48 hours and doesn't get you price-gouged.",
    date: null, status: "idea",
  },
  {
    slug: "quality-tiers-in-chinese-factories",
    title: "Economy, standard, premium: how quality tiers really work in Chinese factories",
    summary: "Same factory, three product tiers. How to ask for the right one without spending their patience.",
    date: null, status: "idea",
  },
  {
    slug: "trade-show-vs-market-sourcing",
    title: "Trade show vs wholesale market: which one does your China trip actually need?",
    summary: "Where each is stronger, and the honest pattern for combining both in one trip.",
    date: null, status: "idea",
  },
  {
    slug: "how-voltage-and-gas-specs-break-projects",
    title: "How voltage, gas type and plug standards quietly break restaurant and kitchen projects",
    summary: "A pre-order checklist for hospitality equipment buyers, so commissioning doesn't surprise you.",
    date: null, status: "idea",
  },
  {
    slug: "what-goes-wrong-in-sampling-rounds",
    title: "What actually goes wrong in sampling rounds — and how to keep them to two",
    summary: "Round structure, who approves what, and the deadline most buyers miss.",
    date: null, status: "idea",
  },
  {
    slug: "small-brand-shopping-in-yiwu",
    title: "Is Yiwu worth visiting for a small brand? An honest split",
    summary: "When the wholesale market beats factory-direct — and when it definitely doesn't.",
    date: null, status: "idea",
  },
  {
    slug: "how-third-party-inspection-works",
    title: "How third-party inspection works: WHO inspects, what AQL means, what 'passed' doesn't mean",
    summary: "The mechanics of pre-shipment inspection, and what nobody tells first-time buyers.",
    date: null, status: "idea",
  },
  {
    slug: "chinese-new-year-sourcing-calendar",
    title: "Chinese New Year and your order: the sourcing calendar nobody warns you about",
    summary: "Why production slows in January–February and how to schedule a trip that doesn't fight the calendar.",
    date: null, status: "idea",
  },
  {
    slug: "how-to-compare-oem-quotes",
    title: "OEM vs ODM vs stock program: which quote are you actually looking at?",
    summary: "The same 'supplier quote' hides three different businesses. How to name yours precisely.",
    date: null, status: "idea",
  },
  {
    slug: "working-with-trading-companies-honestly",
    title: "Should you avoid trading companies? A fair look at when they're the better buy",
    summary: "Trading layers aren't a scam — they solve scale problems. When each structure serves you.",
    date: null, status: "idea",
  },
  {
    slug: "translation-gaps-that-cost-orders",
    title: "Six translation gaps that cost orders in China sourcing meetings",
    summary: "Where plain interpreting isn't enough, and how to brief an interpreter properly.",
    date: null, status: "idea",
  },
  {
    slug: "visit-days-by-category-district",
    title: "One-day routes by industry: what a realistic visit day looks like in each district",
    summary: "Guangzhou–Foshan, Shenzhen, Yiwu, Keqiao: stops per day, realistic drive windows.",
    date: null, status: "idea",
  },
  {
    slug: "payment-safeguards-for-first-orders",
    title: "Payment safeguards for a first China order — deposit protection that is real, not theater",
    summary: "How far you can push payment terms on a first order without losing the factory.",
    date: null, status: "idea",
  },
  {
    slug: "certifications-copy-vs-original-documents",
    title: "Certification copies on a factory wall vs documents that matter",
    summary: "Which certificates exist legitimately and how to ask for the originals.",
    date: null, status: "idea",
  },
  {
    slug: "when-you-dont-need-a-sourcing-agent",
    title: "When you don't need a sourcing agent at all — and where to spend instead",
    summary: "Cases where DIY, Alibaba verified suppliers, or a different helper saves more money.",
    date: null, status: "idea",
  },
  {
    slug: "shipping-from-china-customs-pitfalls",
    title: "Shipping from China: the five customs pitfalls that sink new importers",
    summary: "HS codes, declared values, packing lists and who owns customs liability.",
    date: null, status: "idea",
  },
  {
    slug: "hotel-amenities-sourcing-china",
    title: "Sourcing guest amenities and linens for hotels in China: which markets, which MOQs",
    summary: "An unglamorous category, priced honestly and bought correctly.",
    date: null, status: "idea",
  },
  {
    slug: "auto-parts-visits-ruian-ningbo",
    title: "Auto parts sourcing: why Ruian and Ningbo look similar and behave differently",
    summary: "District-level quirks for aftermarket buyers: quality tiers, minimums, warranty dispatch.",
    date: null, status: "idea",
  },
  {
    slug: "pet-products-sourcing-compliance",
    title: "Pet products: what compliance actually applies to toys, carriers and grooming tools",
    summary: "Destination-market basics for non-food pet goods, and what to verify with a lab.",
    date: null, status: "idea",
  },
  {
    slug: "cosmetic-oem-audit-checklist",
    title: "Cosmetic OEM visits: an honest audit checklist you can use with a non-expert team",
    summary: "What a non-technical founder can verify on site — and what truly requires a specialist.",
    date: null, status: "idea",
  },
  {
    slug: "fashion-sampling-calendar-china",
    title: "Fashion trips: your sampling calendar vs China's reality",
    summary: "Design freeze, sample loops, dye-lot waits — and the days that break the timeline.",
    date: null, status: "idea",
  },
  {
    slug: "electronics-cert-firewall",
    title: "Certification firewall for electronics: what CE/FCC logo copies are worth vs documents",
    summary: "The paperwork mechanics for marketplaces, plus what a real CB report contains.",
    date: null, status: "idea",
  },
  {
    slug: "how-referral-and-commission-work",
    title: "How supplier referral and commission arrangements actually work — disclosed properly",
    summary: "A transparent look at formal relationships, disclosure and why it doesn't shift our shortlists.",
    date: null, status: "idea",
  },
  {
    slug: "trade-show-registration-explained",
    title: "China trade show registration, explained — including what 'official' actually claims",
    summary: "Pre-registering, badge collection, invitation letters, and how to avoid scam bureaus.",
    date: null, status: "idea",
  },
  {
    slug: "choosing-between-guangzhou-shanghai-trip",
    title: "Guangzhou or Shanghai as your China sourcing base city? A decision guide",
    summary: "Category clustering, travel legs, and how a second base city is normally added.",
    date: null, status: "idea",
  },,
{ slug: "verified-supplier-badges-trust", title: "'Verified supplier' badges: what they do and don't guarantee",
  summary: "What platform verification actually covers, which checks remain on you, and the three signals that matter more than the badge.", date: null, status: "idea" },
{ slug: "cross-checking-supplier-filings", title: "Cross-checking a supplier in three steps: filings, footprint, invoices",
  summary: "Registration info, satellite view and invoice lines narrow most supplier claims to fact — or fiction.", date: null, status: "idea" },
{ slug: "mold-ownership-in-china-quotes", title: "Mold ownership: the line that decides whether your repeat order happens at all",
  summary: "How tooling ownership is handled in practice and how to write it into your first quote.", date: null, status: "idea" },
{ slug: "fob-cif-exw-what-changes-price", title: "FOB vs CIF vs EXW: what each includes and where buyers pay twice",
  summary: "Incoterms in practice — what compares cleanly and where a lower 'quote' becomes a higher landed cost.", date: null, status: "idea" },
{ slug: "sample-rounds-to-two", title: "Cutting sample rounds from five to two, without skipping the checks",
  summary: "What to lock in round one so round two confirms only — and the deadline most buyers miss.", date: null, status: "idea" },
{ slug: "lead-time-slippage-third-week", title: "Lead time slipping? The three questions worth asking in week three",
  summary: "A milestone discipline for remote buyers — and the supplier answers that separate real delay from noise.", date: null, status: "idea" },
{ slug: "supplier-vetting-questions-that-work", title: "14 supplier-vetting questions that actually discriminate (and 4 that don't)",
  summary: "Screening questions that separate manufacturers from resellers without burning anyone's patience.", date: null, status: "idea" },
{ slug: "china-procurement-timezone-rhythm", title: "Managing China suppliers from another timezone: a rhythm that works",
  summary: "Communication windows, send-time discipline and how decisions avoid dying in overnight queues.", date: null, status: "idea" },
{ slug: "when-to-fly-to-china-vs-remote-first", title: "When you actually need to fly to China — and when remote-first is enough",
  summary: "Which sourcing decisions deserve a trip, so visits stay strategic instead of reflexive.", date: null, status: "idea" },
{ slug: "protecting-designs-weak-nda", title: "Protecting designs when your NDA is weak: what actually works",
  summary: "Practical constraints small brands use: module design, artwork control, staged disclosure.", date: null, status: "idea" },
{ slug: "reading-a-proforma-invoice", title: "Reading a proforma invoice line by line — and what's usually missing",
  summary: "A PI is a contract skeleton; the seven lines we check first and what each miss costs downstream.", date: null, status: "idea" },
{ slug: "consolidation-mixed-containers", title: "Consolidation: how multi-supplier orders even out your landed cost",
  summary: "Loading plans, carton equity, and when one mixed container beats three LCLs.", date: null, status: "idea" },
];
