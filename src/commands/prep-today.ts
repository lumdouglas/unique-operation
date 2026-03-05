/**
 * /prep-today — Posts 3 embeds to #chef-view, #prep-view, #pack-view
 */

import { SlashCommandBuilder, type ChatInputCommandInteraction } from 'discord.js';
import { getTodayOrdersWithDetails } from '../lib/order-service.js';
import {
  buildChefView,
  buildPrepView,
  buildPackView,
} from '../lib/prep-calculator.js';
import {
  buildChefEmbed,
  buildPrepEmbed,
  buildPackEmbed,
} from '../lib/embeds.js';
import { config } from '../config.js';

export const data = new SlashCommandBuilder()
  .setName('prep-today')
  .setDescription('Post today\'s prep lists to Chef / Prep / Pack channels');

export async function execute(interaction: ChatInputCommandInteraction) {
  await interaction.deferReply({ ephemeral: true });

  const date = new Date().toISOString().slice(0, 10);
  const orders = await getTodayOrdersWithDetails(date);

  const chefItems = buildChefView(orders);
  const prepItems = buildPrepView(orders);
  const packItems = buildPackView(orders);

  const chefEmbed = buildChefEmbed(date, chefItems);
  const prepEmbed = buildPrepEmbed(date, prepItems);
  const packEmbed = buildPackEmbed(date, packItems);

  try {
    const client = interaction.client;
    const chefChannel = await client.channels.fetch(
      config.discord.chefViewChannelId
    );
    const prepChannel = await client.channels.fetch(
      config.discord.prepViewChannelId
    );
    const packChannel = await client.channels.fetch(
      config.discord.packViewChannelId
    );

    if (!chefChannel?.isSendable() || !prepChannel?.isSendable() || !packChannel?.isSendable()) {
      await interaction.editReply({
        content: 'One or more channels (#chef-view, #prep-view, #pack-view) are not configured or not sendable.',
      });
      return;
    }

    await chefChannel.send({ embeds: [chefEmbed] });
    await prepChannel.send({ embeds: [prepEmbed] });
    await packChannel.send({ embeds: [packEmbed] });

    const totalOrders = orders.length;
    const totalServings = orders.reduce((s, o) => s + o.servings, 0);
    await interaction.editReply({
      content: `✅ Posted prep lists to #chef-view, #prep-view, #pack-view\n**${totalOrders}** order(s) · **${totalServings}** total servings`,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await interaction.editReply({
      content: `Failed to post embeds: ${msg}`,
    });
  }
}
