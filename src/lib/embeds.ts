/**
 * Discord embeds for Chef / Prep / Pack views.
 */

import { EmbedBuilder } from 'discord.js';
import type { ChefViewItem, PrepViewItem, PackViewItem } from './prep-calculator.js';

const EMBED_COLOR_CHEF = 0xe74c3c; // red
const EMBED_COLOR_PREP = 0x3498db; // blue
const EMBED_COLOR_PACK = 0x2ecc71; // green

/** Chef view: procedures and total servings per recipe */
export function buildChefEmbed(
  date: string,
  items: ChefViewItem[]
): EmbedBuilder {
  const lines: string[] = [];
  for (const item of items) {
    lines.push(`**${item.recipeName}** — ${item.totalServings} servings`);
    for (const p of item.procedures) {
      lines.push(`  [${p.role}] ${p.step}`);
    }
    lines.push('');
  }
  const description = lines.length ? lines.join('\n') : '_No orders for today._';
  return new EmbedBuilder()
    .setColor(EMBED_COLOR_CHEF)
    .setTitle(`👨‍🍳 Chef View — ${date}`)
    .setDescription(description)
    .setTimestamp();
}

/** Prep view: scaled ingredient quantities */
export function buildPrepEmbed(
  date: string,
  items: PrepViewItem[]
): EmbedBuilder {
  const lines: string[] = [];
  for (const item of items) {
    const qty = formatQuantity(item.totalQuantity);
    const flag = item.lowStock ? ' ⚠️ LOW STOCK' : '';
    lines.push(`• **${item.ingredientName}** — ${qty} ${item.unit}${flag}`);
  }
  const description = lines.length ? lines.join('\n') : '_No prep needed._';
  return new EmbedBuilder()
    .setColor(EMBED_COLOR_PREP)
    .setTitle(`🥒 Prep View — ${date}`)
    .setDescription(description)
    .setTimestamp();
}

/** Pack view: menu summary for packing */
export function buildPackEmbed(
  date: string,
  items: PackViewItem[]
): EmbedBuilder {
  const lines: string[] = [];
  for (const item of items) {
    lines.push(`• **${item.recipeName}** — ${item.totalServings} servings (${item.orderCount} order${item.orderCount > 1 ? 's' : ''})`);
    for (const note of item.notes) {
      if (note) lines.push(`  _${note}_`);
    }
  }
  const description = lines.length ? lines.join('\n') : '_No orders to pack._';
  return new EmbedBuilder()
    .setColor(EMBED_COLOR_PACK)
    .setTitle(`📦 Pack View — ${date}`)
    .setDescription(description)
    .setTimestamp();
}

function formatQuantity(n: number): string {
  if (Number.isInteger(n)) return String(n);
  return n.toFixed(2).replace(/\.?0+$/, '');
}
