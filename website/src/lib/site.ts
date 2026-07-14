/** Canonical site config used across the public website.
 *  Values mirror the Django `systemConfig` key "site" (GET /api/site-config).
 *  These are used as sensible defaults / fallbacks so the UI renders even
 *  before the API response resolves on the server. */
export const site = {
  name: "Royal Priesthood Embassy",
  shortName: "Royal Priesthood",
  tagline: "Discover Your True Identity in Christ",
  scripture: "1 Peter 2:9",
  description:
    "Join Royal Priesthood Embassy in Thika, Kenya. A Kingdom Embassy where you are equipped to establish heaven on earth through worship, discipleship, and authentic relationships.",
  address: {
    street: "Voice of Grace, Behind Spoonzoom",
    city: "Thika",
    country: "Kenya",
    mapsUrl: "https://maps.app.goo.gl/PLHU6uvwqJHPG9PD6",
  },
  contact: {
    email: "enquiries@rp.church",
    whatsapp: "https://wa.me/254700000000",
  },
  social: {
    instagram: "https://www.instagram.com/royalpriesthoodembassy",
    facebook: "https://www.facebook.com/people/Royal-Priesthood-Embassy/61575460188005/",
    youtube: "https://www.youtube.com/@RoyalPriesthoodEmbassy",
  },
  giving: {
    mpesaTill: "8598004",
    accountName: "Salome Njuguna Waruguru",
  },
  academyUrl: "https://rpacademy.vercel.app/",
  theme2026: {
    title: "The Latter Rain",
    scripture: "Zechariah 10:1",
    scriptureText:
      "Ask the LORD for rain in the time of the latter rain. The LORD will make flashing clouds; He will give them showers of rain, Grass in the field for everyone.",
    image: "/images/posters/theme-2026-latter-rain.jpeg",
  },
} as const;

export type NavLink = { label: string; href: string };

export const navLinks: { primary: NavLink[]; media: NavLink[]; connect: NavLink[] } = {
  primary: [
    { label: "About", href: "/about" },
    { label: "Sermons", href: "/sermons" },
    { label: "Visit", href: "/visit" },
    { label: "Events", href: "/events" },
    { label: "Academy", href: "/academy" },
    { label: "Partner", href: "/give" },
  ],
  media: [{ label: "Sermons", href: "/sermons" }],
  connect: [
    { label: "Contact", href: "/contact" },
    { label: "Prayer Request", href: "/prayer" },
  ],
};

export const footerColumns = [
  {
    title: "About",
    links: [
      { label: "Our Vision", href: "/about" },
      { label: "Statement of Faith", href: "/about#beliefs" },
      { label: "Leadership", href: "/about#leadership" },
    ],
  },
  { title: "Media", links: [{ label: "Sermons", href: "/sermons" }] },
  {
    title: "Connect",
    links: [
      { label: "Plan Your Visit", href: "/visit" },
      { label: "Events", href: "/events" },
      { label: "Contact", href: "/contact" },
      { label: "Prayer Request", href: "/prayer" },
      { label: "Give", href: "/give" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy Policy", href: "/privacy" },
      { label: "Terms of Service", href: "/terms" },
    ],
  },
];

// Re-export images from images.ts for convenience
export { images } from "./images";