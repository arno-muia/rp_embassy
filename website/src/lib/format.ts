export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function formatEventDate(dateString: string): string {
  return formatDate(dateString);
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function eventSlug(title: string, id: string): string {
  const base = slugify(title);
  return base ? `${base}-${id.slice(0, 8)}` : id.slice(0, 8);
}

export function leaderInitials(name: string): string {
  return name
    .split(" ")
    .filter((part) => part.length > 1 && !["Pastor", "Pst."].includes(part))
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}