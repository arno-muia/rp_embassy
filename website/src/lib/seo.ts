import { site } from "./site";

export function churchSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "Church",
    name: site.name,
    description: site.description,
    url: "https://rpwebsite.vercel.app",
    address: {
      "@type": "PostalAddress",
      streetAddress: site.address.street,
      addressLocality: site.address.city,
      addressCountry: site.address.country,
    },
    sameAs: [site.social.facebook, site.social.instagram, site.social.youtube],
  };
}