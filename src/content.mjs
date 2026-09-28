// gochina.events content data.
// Rule: every unverified business fact is explicitly marked. No fabricated
// companies, testimonials, prices, dates or team members.

export const SITE = {
  name: "goChina Events",
  domain: "https://gochina.events",
  tagline: "China supply-chain development for overseas companies — supplier research, vetting, samples, factory audits (coordinated) and orders managed end-to-end",
  contact: {
    email: "contact@gochina.events",
    whatsapp: "+86 182 2441 6343",
    whatsappLink: "https://wa.me/8618224416343",
    hours: "Mon–Sun 8:30–19:00 (China Standard Time)",
  },
  description:
    "We develop China supply chains for overseas companies: supplier research and vetting, quote comparison, factory audits (coordinated), sampling and sample rounds, order milestones, pre-shipment inspection — remote from day one, with on-the-ground trips in Guangzhou-Foshan and Shanghai when buyers visit.",
  // Unconfirmed on purpose — resolved before public launch:
  pendingFacts: {
    legalEntity: "Operating entity, registered name and contact details are being confirmed and are not published yet.",
  },
};

export const NAV = [
  { href: "/trade-shows/", label: "Trade Shows" },
  { href: "/industries/", label: "Industries" },
  { href: "/services/", label: "Services" },
  { href: "/business-trips/", label: "Business Trips" },
  { href: "/buyer-meetups/", label: "Buyer Meetups" },
];

export const FOOTER_COLS = [
  {
    title: "Plan",
    links: [
      { href: "/plan-your-trip/", label: "Plan My Trip (inquiry)" },
      { href: "/how-it-works/", label: "How it works" },
      { href: "/pricing/", label: "Pricing & fees" },
      { href: "/destinations/", label: "Cities" },
      { href: "/guides/", label: "Guides" },
    ],
  },
  {
    title: "Trust",
    links: [
      { href: "/supplier-selection/", label: "How we screen suppliers" },
      { href: "/commercial-disclosure/", label: "Commercial disclosure" },
      { href: "/about/", label: "About & team" },
      { href: "/case-studies/", label: "Case studies" },
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

// ---------------------------------------------------------------------------
// Industries (8 lines, all live at launch; content depth grows with verified
// local resources. Each page answers: who this is for, what we can arrange,
// which shows, what to prepare.)
// ---------------------------------------------------------------------------

export const INDUSTRIES = [
  {
    slug: "furniture-building-materials",
    name: "Furniture, Home & Building Materials",
    short: "Furniture, cabinetry, lighting, doors & windows, sanitary ware, decor",
    buyerFit: [
      "Furniture importers and retailers expanding their supplier base",
      "Interior designers and contractors furnishing apartments, hotels or offices",
      "Small hotel, restaurant and retail project owners buying furniture and fittings",
    ],
    whatWeArrange: [
      "Showroom days in Guangzhou, Foshan (Lecong furniture market) and nearby clusters",
      "Factory visits for case goods, upholstery, custom cabinetry and lighting",
      "Sample checks, material and finish comparisons, priced specification lists",
      "Combined container or LCL shipment coordination with freight partners",
    ],
    shows: ["canton-fair", "ciff-guangzhou", "furniture-china"],
    sourcingNotes:
      "Furniture is rarely judged well from photos: material, joinery, foam density, finish and packing all need to be seen. Most projects compare three or more suppliers, so we build visit routes around your product list and MOQ rather than generic showroom tours.",
  },
  {
    slug: "hospitality-equipment",
    name: "Hospitality & Restaurant Equipment",
    short: "Kitchen equipment, refrigeration, furniture, tableware, coffee & bakery lines",
    buyerFit: [
      "Owners opening or renovating restaurants, cafés, bakeries and small hotels",
      "Equipment distributors and dealers looking for new factory sources",
      "Project buyers fitting out multiple outlets or rooms",
    ],
    whatWeArrange: [
      "Equipment showroom and factory visits around Guangzhou, Foshan and Shanghai",
      "Technical discussions with factory engineers (voltage, gas type, certification)",
      "Consolidated quotes across kitchen, refrigeration, furniture and tableware ranges",
      "Packing, container loading and installation-support documentation",
    ],
    shows: ["canton-fair", "hotelex-shanghai"],
    sourcingNotes:
      "Commercial kitchens need matched configuration, not single-item prices. Voltage (220V vs 110V), gas type, plug standards, certification and spare-parts supply change which factory can serve you — we put these questions into every meeting, not just the price.",
  },
  {
    slug: "beauty-packaging",
    name: "Beauty Packaging, Tools & OEM",
    short: "Bottles & jars, pumps, brushes, applicators, cosmetic OEM/ODM",
    buyerFit: [
      "Beauty brands sourcing primary packaging and components",
      "Distributors sourcing brushes, tools and accessories",
      "Brands evaluating cosmetic OEM/ODM manufacturing",
    ],
    whatWeArrange: [
      "Packaging factory visits (glass, plastic, tubes, pumps) around Jiangsu, Zhejiang and Guangdong",
      "Sampling and decoration discussions: printing, frosting, coating, MOQ tiers",
      "OEM/ODM plant audits with our technical partners where required",
      "Component compatibility checks (pump–bottle fits, refill systems)",
    ],
    shows: ["china-beauty-expo", "canton-fair"],
    sourcingNotes:
      "Component tolerance and decoration quality decide repeat orders. We help you compare like with like: resin/grade, decoration method, mold ownership, sample lead time and the actual price at your order quantity — not the showroom minimum.",
  },
  {
    slug: "pet-products",
    name: "Pet Products",
    short: "Toys, bedding, grooming, collars & leashes, carriers, aquarium supplies",
    buyerFit: [
      "Pet brands and private-label sellers planning new ranges",
      "Importers and retail chains looking for manufacturing sources",
      "E-commerce sellers testing products before scaling",
    ],
    whatWeArrange: [
      "Supplier shortlisting by product type, materials and compliance needs",
      "Factory visits in Zhejiang, Jiangsu and Shandong clusters (e.g. around Pingyang, Yangzhou)",
      "Sample rounds and trend assortment reviews",
      "Compliance document checks with testing partners where relevant",
    ],
    shows: ["cips", "canton-fair"],
    sourcingNotes:
      "Pet goods buyers care about safety standards per destination market (e.g. toy material restrictions, textile labels) and stable repeat production. We flag which questions need a lab test versus a factory answer, and do not sell guesses as verified compliance.",
  },
  {
    slug: "automotive-aftermarket",
    name: "Automotive Aftermarket & Repair Equipment",
    short: "Parts, accessories, workshop tools, lifts, diagnostic & body-shop equipment",
    buyerFit: [
      "Parts distributors and chains sourcing ranges by car model or system",
      "Workshop owners buying lifts, testers, alignment and body-shop equipment",
      "Accessories importers (interior, exterior, care products)",
    ],
    whatWeArrange: [
      "Matched factory visits by product category and quality tier",
      "Model and fitment discussions with technical interpreters",
      "Quality-tier comparison (economy vs standard vs premium lines)",
      "Packaging and Mixed-container loading for wide catalogs",
    ],
    shows: ["automechanika-shanghai", "canton-fair"],
    sourcingNotes:
      "This category depends on correct SKU matching and consistent quality between orders. We stay in the coordination role and rely on technically qualified partners for engineering judgments; claims beyond that scope are labelled as such.",
  },
  {
    slug: "industrial-machinery",
    name: "Industrial & Manufacturing Equipment",
    short: "Packaging machinery, food processing, plastics, CNC and production lines",
    buyerFit: [
      "Factory owners investing in production or packaging equipment",
      "Equipment dealers and service agents seeking new principals",
      "Operations teams comparing machine configurations before tender",
    ],
    whatWeArrange: [
      "Supplier research and pre-qualification with technical partners",
      "Factory and live machine demonstrations scheduling",
      "Technical negotiation support: configuration, tooling, spares, warranty terms",
      "Installation-site logistics questions coordinated with the factory",
    ],
    shows: ["canton-fair", "chinaplas"],
    sourcingNotes:
      "Machine purchases live or die on configuration, testing protocol and after-sales. We schedule live demonstrations where possible, record every agreed specification, and treat machine selection as a technical decision supported by specialists — not ours to promise.",
  },
  {
    slug: "fashion-textiles",
    name: "Fashion, Textiles, Shoes & Bags",
    short: "Apparel, fabrics, trims, footwear, bags, sampling and small-batch runs",
    buyerFit: [
      "Clothing and accessory brands developing new collections",
      "Wholesalers sourcing stock programs and fabrics",
      "Brands needing sampling, grading and production follow-up",
    ],
    whatWeArrange: [
      "Fabric and trim market routes in Guangzhou, Keqiao (Shaoxing) and Shanghai",
      "Garment, footwear and bag factory visits matched to your style list",
      "Sampling coordination and size/spec discussion with supplier teams",
      "Production-schedule tracking with agreed check-ins after the trip",
    ],
    shows: ["intertextile-shanghai", "canton-fair"],
    sourcingNotes:
      "Fashion sourcing is a follow-up business: samples, comments, revised samples and shipment checks. Tell us your calendar (design freeze, delivery date) and we plan visits and the after-trip coordination around it.",
  },
  {
    slug: "electronics-general-merchandise",
    name: "Consumer Electronics & General Merchandise",
    short: "Consumer electronics, accessories, housewares, gifts, seasonal items",
    buyerFit: [
      "E-commerce sellers and small importers sourcing catalog goods",
      "Electronics buyers comparing manufacturers and certifications",
      "General merchandise buyers combining many small categories",
    ],
    whatWeArrange: [
      "Electronics factory visits with certification questions on the agenda",
      "Yiwu and Guangzhou wholesale market routes for general merchandise",
      "Supplier screening against your price band and compliance needs",
      "Mixed-category consolidation planning before the trip",
    ],
    shows: ["canton-fair", "global-sources-hong-kong"],
    sourcingNotes:
      "Low-price categories are transparent, so the value is in discipline: unit price at your quantity, packaging, certification for your market, and honest comparison between factory-direct and trading-company offers. Low-budget trips are kept lean so service costs stay proportionate.",
  },
];

// ---------------------------------------------------------------------------
// Services (9)
// ---------------------------------------------------------------------------

export const SVC_ORDER = [
  "supplier-research", "purchasing-coordination", "inspection-logistics-coordination",
  "factory-visits", "business-interpreters", "trade-show-assistance",
  "airport-transfers", "business-transport", "hotel-arrangements",
];

export const SERVICES = [
  {
    slug: "airport-transfers",
    name: "Airport Transfers",
    short: "Meet-and-greet and private transfers between airport, hotel and trade fair venues.",
    audience: "Any overseas visitor arriving for a trade show, sourcing trip or business meetings.",
    includes: [
      "Flight tracking and driver assignment for arrival and departure",
      "Private car or van sized to people and luggage",
      "English-speaking driver or coordinator where available (stated before booking)",
    ],
    excludes: [
      "Visa or immigration advice",
      "Waiting time beyond the agreed free window (quoted in advance)",
    ],
    pricingNote: "Quoted per transfer, fixed price by route and vehicle class. Airport parking and tolls included; night surcharge where applicable is stated in the quote.",
  },
  {
    slug: "business-transport",
    name: "Business Vehicle & Driver Hire",
    short: "Licensed business cars and minivans with drivers, by day or itinerary, for factory visits and multi-stop days.",
    audience: "Buyers touring factories and markets; small teams with supplier visit schedules.",
    includes: [
      "Route planning around your visit list (distance and drive-time warnings)",
      "Driver with local knowledge of industrial areas",
      "Interstate/city-to-city trips quoted separately",
    ],
    excludes: [
      "Unscheduled waiting beyond daily agreed hours (overtime rate stated in quote)",
      "Interpreting — driver is not assumed to interpret business meetings",
    ],
    pricingNote: "Daily hire with a stated number of hours and km; extra hours or km priced in the quote. Vehicle class options and photos provided before confirmation.",
  },
  {
    slug: "hotel-arrangements",
    name: "Hotel Arrangements",
    short: "Hotel shortlisting and booking support near your tradeshow or factory route.",
    audience: "Buyers who want sensible locations for show access and supplier visits, not just the cheapest listing.",
    includes: [
      "2–3 hotel options by location, budget band and availability",
      "Booking support and confirmation handling",
      "Fair-period booking constraints communicated in advance",
    ],
    excludes: [
      "Hotel payments unless explicitly agreed — normally you pay the hotel directly",
      "Room-rate guarantees we do not control",
    ],
    pricingNote: "Planning is usually included in a trip package; standalone booking support is quoted. Where we have hotel cooperation terms, that is disclosed in line with our commercial disclosure page.",
  },
  {
    slug: "business-interpreters",
    name: "Business Interpreters",
    short: "English–Chinese business interpreters for meetings, factory visits and negotiations.",
    audience: "Buyers negotiating specifications, prices and terms with suppliers in person.",
    includes: [
      "Interpreter matched to industry and meeting type (stated before confirmation)",
      "Preparation briefing: your product list, goals and question set",
      "Written notes of decisions and open items after each meeting day (where included in package)",
    ],
    excludes: [
      "Legal, certification or deep engineering judgment — these need a specialist and we say so up front",
      "Simultaneous conference interpreting (a different, more expensive service)",
    ],
    pricingNote: "Day rate by duration, city and technical level; overtime and travel days stated in quote. Quality varies in this market, so we name the interpreter's background before you confirm.",
  },
  {
    slug: "trade-show-assistance",
    name: "Trade Show Registration & On-Site Support",
    short: "Registration guidance, badge assistance, show planning and on-site coordination.",
    audience: "First-time and returning visitors who want the show handled without guesswork.",
    includes: [
      "Registration route for the specific fair (many are free pre-registered; we do not resell tickets)",
      "Show plan: hall priorities matched to your product list",
      "On-site support days: interpreter + coordinator for meetings and walk-through",
    ],
    excludes: [
      "Reselling official tickets or claiming official organizer status",
      "Booth design/build — we can introduce an exhibition service company instead",
    ],
    pricingNote: "Quoted as a per-show support package based on days needed; official fees you pay directly to the organizer.",
  },
  {
    slug: "supplier-research",
    name: "Supplier Research & Vetting",
    short: "Verified candidate shortlists: capability, evidence, MOQ, open questions — built remotely, before you spend anything.",
    audience: "Buyers entering a new category or expanding a China supply chain who need a defensible shortlist, not directory noise.",
    includes: [
      "Candidate sourcing across directories, trade platforms, market channels and referral lines",
      "Structured screening: product fit at your volume, MOQ/possible Mixed orders, export experience, certifications claimed vs documented",
      "Evidence notes per candidate: what was checked, when, what remains unverified",
      "Shortlist delivered as a comparison-ready document with per-supplier open questions",
      "Optional: first-contact outreach in Chinese, quote collection at your quantity",
    ],
    excludes: [
      "Factory audits or certification verification — coordinated via accredited third-party partners at their fees",
      "Guaranteed prices — we report quoted ranges at your quantity, not market prediction",
      "Any claim of 'verified quality' — quality claims stay with inspectors, our deliverable is documented research",
    ],
    pricingNote: "Quoted per category, list depth and whether supplier outreach is included. Delivered remotely in an agreed format — see supply-chain kickoff structure on the pricing page. This is the core service behind our /pricing/ supply-chain kickoff card.",
  },
  {
    slug: "purchasing-coordination",
    name: "Purchasing & Order Coordination",
    short: "Keep quotes, samples, contracts and orders moving — milestone by milestone, without another flight.",
    audience: "Buyers working with one or more Chinese suppliers who need steady execution between visits.",
    includes: [
      "Quote chase-up with a structured comparison against your brief",
      "Sample rounds managed: request logic, shipping, feedback loops, revision checks",
      "Order-stage coordination: contract/spec consistency, milestone reminders, document checklists",
      "Milestone reports you can forward to your own management without rewording",
    ],
    excludes: [
      "Taking ownership of goods or acting as importer of record",
      "Contracting as your legal representative — contracts are signed between you and your supplier",
      "Replaceable functions of third-party inspection, which we coordinate but do not perform",
    ],
    pricingNote: "Retainer or per-milestone packages, scoped up front. Works fully remote; pairs naturally with a factory-visit block when you travel.",
  },
  {
    slug: "factory-visits",
    name: "Showroom & Factory Visits",
    short: "Scheduled visits to the right factories and showrooms, with the right people present.",
    audience: "Buyers who need to see material, machinery and working conditions before ordering.",
    includes: [
      "Supplier confirmation: capacity, willingness to host small/new orders, contact level",
      "Route planning by district to avoid cross-city zig-zag",
      "Accompanied visits with structured question lists and records",
    ],
    excludes: [
      "Unannounced audits — formal audits run through accredited inspection firms",
      "Access we cannot verify — if a factory declines, we tell you rather than stage a visit",
    ],
    pricingNote: "Usually packaged with interpreting and transport per day; standalone scheduling support is quoted by list size.",
  },
  {
    slug: "purchasing-coordination",
    name: "Purchasing Coordination & Follow-Up",
    short: "Keeping quotes, samples and orders moving after your trip ends.",
    audience: "Clients who signed nothing yet gained quotes and samples, and need momentum without another flight.",
    includes: [
      "Quote chase-up and comparison summary against your brief",
      "Sample logistics and feedback loops in agreed rounds",
      "Order-stage coordination: documentation checklists, milestone reminders",
    ],
    excludes: [
      "Taking title to goods or acting as importer of record",
      "Replaceable functions of third-party inspection (we coordinate, they inspect)",
    ],
    pricingNote: "Monthly retainer or per-milestone packages, scoped up front. Contracts are signed between you and the supplier directly; our role is coordination, not contracting.",
  },
  {
    slug: "inspection-logistics-coordination",
    name: "Inspection & Shipping Coordination",
    short: "Third-party inspection and freight arranged and tracked with clear responsibilities.",
    audience: "Buyers who want an independent check before shipment and one point of contact for paperwork.",
    includes: [
      "Booking accredited inspection agencies for defined checkpoints",
      "Freight forwarder options for sea/air/LCL with quotes passed through at actual rates",
      "Coordination of loading, documents and timelines between all parties",
    ],
    excludes: [
      "Our own quality certification — quality conclusions come from the accredited inspector",
      "Duty/customs advice for your country — your broker or forwarder confirms import requirements",
    ],
    pricingNote: "Inspection and freight are pass-through costs at actual provider rates plus a coordination fee stated in advance.",
  },
];

// ---------------------------------------------------------------------------
// Trade shows — start small, real facts only. Dates/venues change every year:
// each page links the official site and shows its last-verified date.
// Checked 2026-09-20: existence and official domains below verified via
// organizer sources during the planning research (see handoff notes).
// ---------------------------------------------------------------------------

export const TRADE_SHOWS = [
  {
    slug: "canton-fair",
    name: "Canton Fair (China Import and Export Fair)",
    city: "Guangzhou",
    venue: "China Import and Export Fair Complex (Pazhou), Guangzhou",
    official: "https://www.cantonfair.org.cn/en-US/index.html",
    cadence: "Twice a year (spring and autumn sessions; three phases per session)",
    phases: "Phase 1: electronics & machinery; Phase 2: consumer goods, gifts & home decor; Phase 3: textiles, footwear, office, medical and chemicals (phases change slightly by session — check the official site).",
    whyFits: "The largest general merchandise sourcing fair; overseas buyers can cover many categories in one trip, then extend into Foshan/Yiwu sourcing days.",
    supportNote: "We help with registration guidance, hotel planning across the three phases, interpreters, and supplier visit days between phases.",
  },
  {
    slug: "ciff-guangzhou",
    name: "CIFF Guangzhou (China International Furniture Fair)",
    city: "Guangzhou",
    venue: "Canton Fair Complex + Poly World Trade Center, Guangzhou",
    official: "https://www.ciff-gz.com/en",
    cadence: "Annually in spring (Guangzhou); the same brand runs a Shanghai edition in autumn",
    phases: "Different halls cover home furniture, office & commercial furniture, furniture machinery and raw materials.",
    whyFits: "The strongest furniture-industry cluster week in Guangzhou, with a natural extension to Foshan showroom sourcing.",
    supportNote: "We combine show days with Foshan (Lecong) showroom days and factory visits for your short-list.",
  },
  {
    slug: "furniture-china",
    name: "Furniture China (Shanghai)",
    city: "Shanghai",
    venue: "Shanghai New International Expo Centre (SNIEC) + Shanghai Expo Centre",
    official: "https://www.furniture-china.cn/",
    cadence: "Annually in September",
    whyFits: "The main furniture show in the Yangtze Delta, convenient for buyers combining Shanghai city suppliers and Suzhou/Hangzhou-area factories.",
    supportNote: "We build show + supplier visit itineraries across the Shanghai region.",
  },
  {
    slug: "hotelex-shanghai",
    name: "HOTELEX Shanghai (Hospitality & Food Expo)",
    city: "Shanghai",
    venue: "Shanghai New International Expo Centre (SNIEC)",
    official: "https://www.hotelex.cn/",
    cadence: "Annually in spring (Shanghai); other editions run in other cities",
    whyFits: "Covers kitchen equipment, coffee supplies, catering and hotel furniture/fittings — a strong anchor for people opening or equipping restaurants and hotels.",
    supportNote: "We plan equipment factory and showroom visits around the show, with technical interpreters for equipment discussions.",
  },
  {
    slug: "china-beauty-expo",
    name: "CBE China Beauty Expo Shanghai",
    city: "Shanghai",
    venue: "Shanghai New International Expo Centre (SNIEC)",
    official: "https://www.chinabeautyexpo.com/en/",
    cadence: "Annually in May",
    whyFits: "The main beauty-industry fair for finished brands, packaging (Cosmopack section) and supply-chain players in China.",
    supportNote: "We extend the fair with packaging/OEM factory visits in Jiangsu/Zhejiang and sampling follow-up.",
  },
  {
    slug: "cips",
    name: "CIPS (China International Pet Show)",
    city: "Held in different cities — confirm the current host city on the official site",
    venue: "Confirm on official site",
    official: "https://en.cipscom.com/",
    cadence: "Annually (autumn)",
    whyFits: "The largest pet-industry fair in Asia, with strong international buyer attendance.",
    supportNote: "We arrange supplier shortlists and factory visits for your product range, plus trip support around the show.",
  },
  {
    slug: "automechanika-shanghai",
    name: "Automechanika Shanghai",
    city: "Shanghai",
    venue: "National Exhibition and Convention Center (NECC), Shanghai",
    official: "https://automechanika-shanghai.messefrankfurt.com/shanghai/en.html",
    cadence: "Annually (usually Nov/Dec)",
    whyFits: "The largest automotive aftermarket and service-station equipment show in the Asia region.",
    supportNote: "We schedule parts-supplier and workshop-equipment visits with appropriate technical interpreting.",
  },
  {
    slug: "chinaplas",
    name: "CHINAPLAS (International Plastics & Rubber Exhibition)",
    city: "Rotates between Shanghai and Shenzhen — confirm the current host on the official site",
    venue: "Confirm on official site",
    official: "https://www.chinaplasonline.com/",
    cadence: "Annually (spring)",
    whyFits: "Key show for plastics machinery, materials and packaging applications.",
    supportNote: "We coordinate machine supplier visits and technical interpretation; equipment judgments stay with specialists.",
  },
  {
    slug: "intertextile-shanghai",
    name: "Intertextile Shanghai Apparel Fabrics",
    city: "Shanghai",
    venue: "National Exhibition and Convention Center (NECC), Shanghai",
    official: "https://shanghai.intertextileapparel.com/",
    cadence: "Twice a year (spring and autumn editions)",
    whyFits: "The main fabric fair for apparel brands and wholesalers, with international mills and Chinese suppliers.",
    supportNote: "We link the fair with fabric market routes (Guangzhou / Keqiao) and sampling follow-up.",
  },
  {
    slug: "global-sources-hong-kong",
    name: "Global Sources Hong Kong Shows",
    city: "Hong Kong",
    venue: "AsiaWorld-Expo / Hong Kong Convention and Exhibition Centre",
    official: "https://www.globalsources.com/",
    cadence: "Twice a year (spring and autumn categories: electronics, lifestyle, etc.)",
    whyFits: "Efficient buying option for electronics and lifestyle goods, often combined with a Guangzhou/Shenzhen sourcing leg.",
    supportNote: "We plan cross-border legs: Hong Kong show + Shenzhen factory days in one trip.",
  },
];

// ---------------------------------------------------------------------------
// Business trips — transparent product pages. Delivery capability determines
// language: things marked as sample sit clearly in a preview lane.
// ---------------------------------------------------------------------------

export const TRIPS = [
  {
    slug: "guangzhou-canton-fair-support",
    name: "Canton Fair Support Package (Guangzhou)",
    status: "active",
    days: "Per quote (typically 3–6 days)",
    cities: "Guangzhou",
    audience: "Buyers attending any phase of the Canton Fair who also want supplier visits between phases.",
    whatIsIncluded: [
      "Trip plan: hotel options near your fair phase, transfer schedule",
      "Registration guidance and on-site support days",
      "Business interpreter for your meeting days",
      "One sourcing day built from your product list (supplier research included)",
    ],
    quoteBasis: "Fixed package price plus pass-through costs (hotel, vehicle, meals) shown separately. Final quote issued after a short planning call.",
  },
  {
    slug: "guangzhou-foshan-furniture-sourcing",
    name: "Guangzhou–Foshan Furniture Sourcing Trip",
    status: "sample",
    days: "3 sourcing days (sample structure)",
    cities: "Guangzhou, Foshan",
    audience: "Furniture and project buyers using CIFF / Canton Fair week, or travelling specifically to source furniture.",
    whatIsIncluded: [
      "Pre-trip: requirement brief, shortlist of 5–8 candidate suppliers/showrooms",
      "Day-by-day visit route across Lecong and selected factories",
      "Accompanied interpreting, records of each visit",
      "Post-trip comparison sheet and follow-up rounds",
    ],
    quoteBasis: "Sample itinerary — the route shown is an example structure, priced per trip after confirming availability of the actual supplier visits.",
  },
  {
    slug: "shanghai-show-support",
    name: "Shanghai Trade Show + Supplier Days",
    status: "sample",
    days: "Per quote (sample structure)",
    cities: "Shanghai (optionally Suzhou/Hangzhou/Ningbo)",
    audience: "Buyers attending HOTELEX, CBE, Automechanika, Intertextile or similar Shanghai shows.",
    whatIsIncluded: [
      "Show planning and registration guidance",
      "Supplier visit days in Shanghai or the Yangtze Delta",
      "Interpreter and transport coordination",
      "Follow-up coordination after the trip",
    ],
    quoteBasis: "Sample itinerary — priced per trip after supplier availability is confirmed.",
  },
];

// ---------------------------------------------------------------------------
// Guides — decision-type articles only (no keyword-variant pages)
// ---------------------------------------------------------------------------

export const GUIDES = [
  {
    slug: "foshan-furniture-first-visit",
    name: "Buying furniture in Foshan: how to prepare your first visit",
    summary: "What a useful Foshan furniture day looks like: product list, MOQs, showroom vs factory, transport and records.",
  },
  {
    slug: "canton-fair-phase-choice",
    name: "Canton Fair phases: how to choose and how to combine phases with factory visits",
    summary: "Phase split by category, why the phase you pick changes your hotel days, and when to add sourcing days.",
  },
  {
    slug: "interpreter-or-sourcing-agent",
    name: "Interpreter vs sourcing agent: which does your trip actually need?",
    summary: "Where an interpreter is enough, where you need supplier development work, and what either role will not do.",
  },
  {
    slug: "what-supplier-visit-costs",
    name: "What a supplier visit day really costs",
    summary: "Cost components for a visit day (vehicle, interpreter, time, distance pitfalls) so quotes can be compared honestly.",
  },
];

// ---------------------------------------------------------------------------
// Buyer Meetups — honest placeholder phase. No invented events/attendees.
// ---------------------------------------------------------------------------

export const MEETUPS = {
  intentCopy: true, // page communicates interest-gathering, no confirmed events yet
};
