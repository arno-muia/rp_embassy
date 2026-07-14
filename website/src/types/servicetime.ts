export interface ServiceTime {
  name: string;
  day: string;
  time: string;
  platform: "physical" | "online";
  location?: string;
  link?: string;
  description?: string;
  image?: string;
}

export interface WhatToExpectItem {
  title: string;
  description: string;
  icon: string;
}